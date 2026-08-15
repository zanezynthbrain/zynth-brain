"""Feature switches — turn autonomous (money-spending) work ON/OFF.

The MD chatbot (free-text chief-of-staff + the commands you type) is ALWAYS on — it
only costs money when you use it. What costs money quietly is the *scheduled* autonomous
work (the daily full-agency brief, proposal production, research, autopilot, etc.). This
module gates all of that behind switches you control from Telegram (/switch, /quiet,
/active) and the dashboard.

Master switch: `autonomy`. When OFF → every scheduled job is skipped (MD-only mode).
Each job also has its own switch for fine control once you turn autonomy back on.

Defaults are OFF (quiet) so a fresh deploy does not burn API budget until you say so.
State persists in the committed pool; the scheduler reads it fresh every run so toggles
take effect immediately.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

_FILE = Path("outputs/proposal_pool/switches.json")

# (key, label, is_master, default_on)
SWITCHES = [
    ("autonomy",              "Autonomous work — MASTER (all scheduled jobs)", True,  False),
    ("morning_brief",         "Daily CEO brief (full agency run — biggest cost)", False, False),
    ("eod_report",            "End-of-day summary",                     False, False),
    ("daily_proposals",       "Daily proposal production (one by one)", False, False),
    ("daily_workforce",       "Daily Agency Workforce (3 founder-reviewable packages)", False, False),
    ("market_research",       "Daily prospect research",                False, False),
    ("bd_autopilot",          "BD autopilot (enrich + draft outreach)", False, False),
    ("outreach_sender",       "Send released outreach",                 False, False),
    ("nightly_consolidation", "Nightly consolidation",                  False, False),
    ("self_improve",          "Weekly self-improvement review",         False, False),
    ("learning_brief",        "Weekly MD learning brief",               False, False),
    ("weekly_reviews",        "Weekly Mon/Fri/portfolio reviews",       False, False),
    ("fx_refresh",            "Daily FX rate refresh",                  False, False),
    ("publisher",             "Publish MD-approved posts at their time", False, True),
    ("brand_creative",        "Nightly brand content/design month",     False, False),
    ("creative_prep",         "Nightly video + 3D brief prep (queued, not generated)", False, False),
]
_DEFAULTS = {k: d for k, _, _, d in SWITCHES}
_LABEL = {k: lbl for k, lbl, _, _ in SWITCHES}
_MASTER = "autonomy"
_VALID = set(_DEFAULTS)


def _load() -> dict:
    if _FILE.exists():
        try:
            return json.loads(_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save(state: dict) -> None:
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    state["_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    _FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def raw_on(name: str) -> bool:
    """The switch's own stored value (ignores the master)."""
    return bool(_load().get(name, _DEFAULTS.get(name, False)))


def enabled(job: str) -> bool:
    """Should a SCHEDULED job run? Requires the master AND the job's own switch on."""
    if job == _MASTER:
        return raw_on(_MASTER)
    return raw_on(_MASTER) and raw_on(job)


def set_switch(name: str, value: bool) -> bool:
    if name not in _VALID:
        return False
    state = _load()
    state[name] = bool(value)
    _save(state)
    return True


def md_only() -> bool:
    """True when only the MD chatbot is active (autonomy master off)."""
    return not raw_on(_MASTER)


def set_quiet() -> None:
    """MD-only mode: silence all autonomous work."""
    set_switch(_MASTER, False)


def set_active() -> None:
    """Wake the autonomous work back up (individual switches still apply)."""
    set_switch(_MASTER, True)


def all_switches() -> list[dict]:
    """For the dashboard + /switch: every switch with its live state."""
    out = []
    for key, label, is_master, _ in SWITCHES:
        out.append({
            "name": key, "label": label, "master": is_master,
            "on": raw_on(key),
            "effective": raw_on(key) if is_master else enabled(key),
        })
    return out


def status_text() -> str:
    mode = "🟢 ACTIVE (autonomous work running)" if raw_on(_MASTER) else "🌙 MD-ONLY (autonomous work paused)"
    lines = [f"<b>Mode:</b> {mode}", ""]
    for s in all_switches():
        if s["master"]:
            continue
        mark = "✅" if s["effective"] else ("🔸" if s["on"] else "⬜️")
        lines.append(f"{mark} <code>{s['name']}</code> — {s['label']}")
    lines.append("")
    lines.append("Toggle: <code>/switch &lt;name&gt; on|off</code> · <code>/quiet</code> (MD-only) · <code>/active</code> (wake all)")
    return "\n".join(lines)
