"""Connection health — does every link in the ZYNTH stack actually work?

The MD asked a fair question: "is everything really connected?" Answering it in
prose is worthless, because prose goes stale the moment something breaks. So
this module *checks*, every time it is called, and reports what it found.

Each check returns a :class:`Link` with a traffic-light status and — when
something is wrong — the exact command that fixes it. Nothing here mutates
state, spends money, or talks to the network: checks are filesystem, env and
git only, so this is safe to run on every dashboard poll.

Statuses
    ok    — working, nothing to do
    warn  — works but degraded (stale data, optional feature off)
    down  — broken or not configured; the thing it enables cannot happen
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

#: Repo root — this file lives at backend/utils/, so up two.
ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"

STALE_GRAPH_DAYS = 3


@dataclass
class Link:
    key: str
    name: str
    status: str            # ok | warn | down
    detail: str
    fix: str = ""
    facts: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _age_days(p: Path) -> float | None:
    try:
        delta = datetime.now(timezone.utc) - datetime.fromtimestamp(
            p.stat().st_mtime, tz=timezone.utc
        )
        return delta.total_seconds() / 86400
    except OSError:
        return None


def _git(*args: str) -> str:
    """Run a read-only git command. Returns '' if git is unavailable."""
    try:
        out = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


# --------------------------------------------------------------------------
# individual checks
# --------------------------------------------------------------------------

def check_github() -> Link:
    """Is the repo wired to a remote, and is local work actually pushed?"""
    if not (ROOT / ".git").exists():
        return Link("github", "GitHub", "down", "Not a git repository.",
                    "Clone the repo properly.")
    branch = _git("branch", "--show-current") or "(detached)"
    remote = _git("remote", "get-url", "origin")
    if not remote:
        return Link("github", "GitHub", "down", "No 'origin' remote configured.",
                    "git remote add origin <url>")

    dirty = _git("status", "--porcelain")
    unpushed = _git("rev-list", "--count", f"origin/{branch}..HEAD") or "0"
    last = _git("log", "-1", "--format=%h %s")
    facts = {"branch": branch, "unpushed": int(unpushed or 0),
             "dirty_files": len([l for l in dirty.splitlines() if l.strip()]),
             "last_commit": last}

    if facts["unpushed"] or facts["dirty_files"]:
        bits = []
        if facts["unpushed"]:
            bits.append(f"{facts['unpushed']} commit(s) not pushed")
        if facts["dirty_files"]:
            bits.append(f"{facts['dirty_files']} uncommitted file(s)")
        return Link("github", "GitHub", "warn",
                    f"On {branch}. " + ", ".join(bits) + ".",
                    f"git add -A && git commit && git push -u origin {branch}", facts)
    return Link("github", "GitHub", "ok",
                f"On {branch}, everything pushed. Last: {last}", "", facts)


def check_obsidian() -> Link:
    """Two vaults exist by design: the bot writes runtime notes into the pool,
    and those are mirrored into the vault Obsidian actually opens. Check both,
    and whether the mirror has fallen behind."""
    opened = ROOT / "vault" / "ZYNTH-OS"          # the vault the MD opens
    runtime = BACKEND / "outputs" / "proposal_pool" / "vault"  # bot writes here

    opened_notes = list(opened.rglob("*.md")) if opened.exists() else []
    runtime_notes = list(runtime.rglob("*.md")) if runtime.exists() else []
    facts = {"vault_path": str(opened.relative_to(ROOT)),
             "notes_in_vault": len(opened_notes),
             "runtime_notes": len(runtime_notes)}

    if not opened.exists():
        return Link("obsidian", "Obsidian vault", "down",
                    "vault/ZYNTH-OS/ does not exist — nothing for Obsidian to open.",
                    "Open the repo's vault/ folder as an Obsidian vault.", facts)

    # Is the mirror current? Compare newest runtime note to newest mirrored note.
    live = opened / "Live"
    newest_runtime = max((_age_days(p) or 999 for p in runtime_notes), default=None)
    newest_live = max((_age_days(p) or 999 for p in live.rglob("*.md")), default=None) \
        if live.exists() else None
    if newest_runtime is not None and newest_live is not None:
        facts["mirror_lag_days"] = round(max(0.0, newest_live - newest_runtime), 2)

    if not opened_notes:
        return Link("obsidian", "Obsidian vault", "warn",
                    "Vault folder exists but has no notes yet.",
                    "Run /mirror in Telegram to populate it.", facts)

    detail = f"{len(opened_notes)} notes in vault/ZYNTH-OS/"
    if runtime_notes:
        detail += f" · {len(runtime_notes)} runtime notes mirrored from the bot"
    return Link("obsidian", "Obsidian vault", "ok", detail, "", facts)


def check_graphify() -> Link:
    """Graphify is three parts: the package, the built graph, and the skill+hook
    that make Claude reach for it. All three must be present, and the graph must
    not be stale — a stale code graph is worse than none, it answers wrongly."""
    installed = shutil.which("graphify") is not None
    if not installed:
        try:
            import graphify  # noqa: F401
            installed = True
        except ImportError:
            installed = False

    skill = (ROOT / ".claude" / "skills" / "graphify" / "SKILL.md").exists()
    settings = ROOT / ".claude" / "settings.json"
    hook = False
    if settings.exists():
        try:
            hook = "graphify" in settings.read_text(encoding="utf-8")
        except OSError:
            hook = False

    # graph.json is the artifact every query reads; the .graphify_* files are
    # intermediate extraction state and are not enough on their own.
    graph = ROOT / "graphify-out" / "graph.json"
    age = _age_days(graph) if graph.exists() else None
    size_mb = round(graph.stat().st_size / 1e6, 1) if graph.exists() else 0

    facts = {"package_installed": installed, "skill": skill, "hook": hook,
             "graph_json": graph.exists(), "graph_mb": size_mb,
             "graph_age_days": round(age, 1) if age is not None else None}

    # Rebuilding is done by the /graphify SKILL, not the CLI — the CLI only
    # queries an existing graph (path / explain / diagnose).
    rebuild = "/graphify . --update   (in a Claude Code session)"

    if not installed:
        return Link("graphify", "Graphify code graph", "down",
                    "Package not installed — no code graph queries possible.",
                    "pip install graphifyy", facts)
    if not graph.exists():
        return Link("graphify", "Graphify code graph", "down",
                    "Installed, but graphify-out/graph.json does not exist — "
                    "nothing to query.", rebuild, facts)
    if age is not None and age > STALE_GRAPH_DAYS:
        return Link("graphify", "Graphify code graph", "warn",
                    f"Graph is {age:.0f} days old ({size_mb} MB) — it will answer "
                    "from stale code. The repo has changed since it was built.",
                    rebuild, facts)
    parts = "package + graph" + (" + skill" if skill else "") + (" + hook" if hook else "")
    return Link("graphify", "Graphify code graph", "ok",
                f"{parts}; graph built {age:.1f} days ago ({size_mb} MB).", "", facts)


def check_claude_api() -> Link:
    """Without a key the whole agency runs in mock mode: it produces
    schema-shaped placeholders, not real work. Worth being loud about."""
    key = os.getenv("ANTHROPIC_API_KEY", "")
    facts = {"configured": bool(key)}
    if not key:
        return Link("claude", "Claude API", "down",
                    "No ANTHROPIC_API_KEY here — agents run in MOCK mode "
                    "(placeholder output, not real work).",
                    "Set ANTHROPIC_API_KEY (it lives in Railway for the live bot).",
                    facts)
    return Link("claude", "Claude API", "ok", "Key present — agents run live.", "", facts)


def check_telegram() -> Link:
    key = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not key:
        return Link("telegram", "Telegram bot", "warn",
                    "No token in this environment (normal for a sandbox — "
                    "the live bot holds it on Railway).",
                    "Set TELEGRAM_BOT_TOKEN on Railway.", {"configured": False})
    return Link("telegram", "Telegram bot", "ok", "Token present.", "", {"configured": True})


def check_drive() -> Link:
    """Drive is the second half of dual storage — GitHub always works, Drive is
    optional and silently off until both secrets exist."""
    sa = bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
    folder = bool(os.getenv("DRIVE_DELIVERABLES_FOLDER"))
    facts = {"service_account": sa, "folder_id": folder}
    if sa and folder:
        return Link("drive", "Google Drive mirror", "ok",
                    "Both secrets set — deliverables copy to Drive.", "", facts)
    missing = [n for n, v in (("GOOGLE_SERVICE_ACCOUNT_JSON", sa),
                              ("DRIVE_DELIVERABLES_FOLDER", folder)) if not v]
    return Link("drive", "Google Drive mirror", "warn",
                "Off — deliverables save to GitHub only. Missing: " + ", ".join(missing),
                "Set both on Railway to switch Drive mirroring on.", facts)


def check_switches() -> Link:
    """Autonomous work is gated. If the master is off, nothing runs on its own —
    which is a valid choice, but the MD should never be surprised by it."""
    try:
        from utils import switches
        master = switches.raw_on("autonomy")
        on = [k for k, _, is_master, _ in switches.SWITCHES
              if not is_master and switches.raw_on(k)]
    except Exception as exc:                                  # pragma: no cover
        return Link("switches", "Autonomous jobs", "down",
                    f"Could not read switches: {exc}", "Check switches.json")

    facts = {"master": master, "jobs_on": on}
    if not master:
        return Link("switches", "Autonomous jobs", "warn",
                    "MASTER OFF — quiet mode. Nothing runs on a schedule; "
                    "the bot only answers when spoken to.",
                    "/active in Telegram, or toggle on the dashboard.", facts)
    if not on:
        return Link("switches", "Autonomous jobs", "warn",
                    "Master on, but every individual job is off.",
                    "/switch <job> on", facts)
    return Link("switches", "Autonomous jobs", "ok",
                f"{len(on)} job(s) running: {', '.join(on)}", "", facts)


def check_creative_queue() -> Link:
    """The bot/session bridge. Depth here is work waiting on the MD."""
    try:
        from utils import creative_queue
        c = creative_queue.counts()
    except Exception as exc:                                  # pragma: no cover
        return Link("queue", "Creative queue", "down",
                    f"Could not read queue: {exc}", "")
    if c["pending"] == 0:
        return Link("queue", "Creative queue", "ok",
                    f"Empty · {c['generated']} generated to date.", "", c)
    return Link("queue", "Creative queue", "warn",
                f"{c['pending']} waiting — {c['image']} image, {c['video']} video, "
                f"{c['scene3d']} 3D. These need a live session to generate.",
                "Open Claude Code and say “drain the creative queue”, or /cqueue export",
                c)


CHECKS = (
    check_github, check_obsidian, check_graphify, check_claude_api,
    check_telegram, check_drive, check_switches, check_creative_queue,
)


def run_all() -> list[Link]:
    """Every check, in display order. A failing check never breaks the report."""
    out: list[Link] = []
    for fn in CHECKS:
        try:
            out.append(fn())
        except Exception as exc:                              # pragma: no cover
            out.append(Link(fn.__name__, fn.__name__, "down",
                            f"Check itself failed: {exc}"))
    return out


def summary() -> dict[str, Any]:
    links = run_all()
    tally = {s: sum(1 for l in links if l.status == s) for s in ("ok", "warn", "down")}
    overall = "down" if tally["down"] else ("warn" if tally["warn"] else "ok")
    return {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall": overall,
        "tally": tally,
        "links": [l.as_dict() for l in links],
    }


def text_report() -> str:
    """Plain-text version for Telegram."""
    icon = {"ok": "🟢", "warn": "🟡", "down": "🔴"}
    s = summary()
    lines = [f"{icon[s['overall']]} <b>Connections</b> — "
             f"{s['tally']['ok']} ok · {s['tally']['warn']} warn · {s['tally']['down']} down", ""]
    for l in s["links"]:
        lines.append(f"{icon[l['status']]} <b>{l['name']}</b>")
        lines.append(f"   {l['detail']}")
        if l["fix"]:
            lines.append(f"   ↳ <code>{l['fix']}</code>")
    return "\n".join(lines)


__all__ = ["Link", "run_all", "summary", "text_report", "CHECKS", "ROOT"]
