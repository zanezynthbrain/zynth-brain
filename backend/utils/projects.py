"""Projects — the unit of work the MD actually thinks in.

Tasks are too small and departments are too broad. What the agency runs is
*projects*: IGNITE, a client campaign, a launch, a retainer month. Each one has
a client, a value, a stage, a date, an owner, and a pile of tasks and
deliverables hanging off it.

IGNITE is one row in this table, not the system. The system is this table.

Storage is JSON under ``outputs/proposal_pool/`` so it rides the same
git-as-database path as the proposal pool and survives Railway redeploys.
Nothing here spends money or talks to the network.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any

_FILE = Path("outputs/proposal_pool/projects.json")

#: Pipeline stages, in order. A project only ever moves along this line.
STAGES = ["lead", "proposal", "won", "delivery", "done", "lost"]

#: Stages that still need work from us.
ACTIVE_STAGES = {"lead", "proposal", "won", "delivery"}

KINDS = [
    "event", "campaign", "content", "video", "retainer", "owned",
    "sponsorship", "digital", "social", "stage_design",
]

_MARKETS = ("MM", "SG")
APPROVAL_STATUSES = ("pending", "approved", "declined", "not_required")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:48] or "project"


def _load() -> list[dict[str, Any]]:
    if not _FILE.exists():
        return []
    try:
        data = json.loads(_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _save(rows: list[dict[str, Any]]) -> None:
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def add(
    name: str,
    *,
    client: str = "",
    kind: str = "event",
    stage: str = "lead",
    value_mmk: float = 0.0,
    market: str = "MM",
    owner: str = "",
    event_date: str = "",
    notes: str = "",
    source: str = "md",
    founder_confirmation_required: bool | None = None,
    founder_approval: str = "",
) -> dict[str, Any]:
    """Create a project. Returns the stored row."""
    name = (name or "").strip()
    if not name:
        raise ValueError("a project needs a name")
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}")
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if market not in _MARKETS:
        raise ValueError(f"market must be one of {list(_MARKETS)}")
    if value_mmk < 0:
        raise ValueError("value cannot be negative")
    if founder_confirmation_required is None:
        # Founder-created records are already intentional. Imported leads and
        # agent discoveries remain blocked until the founder explicitly approves
        # them; a record manually created through the authenticated dashboard is
        # treated as a founder decision.
        founder_confirmation_required = source not in {"md", "seed", "owner", "dashboard"}
    if not founder_approval:
        founder_approval = "pending" if founder_confirmation_required else "not_required"
    if founder_approval not in APPROVAL_STATUSES:
        raise ValueError(f"founder_approval must be one of {APPROVAL_STATUSES}")
    if not founder_confirmation_required and founder_approval == "pending":
        raise ValueError("a record without founder confirmation cannot be pending")

    row = {
        "id": uuid.uuid4().hex[:10],
        "slug": _slug(name),
        "name": name[:120],
        "client": client[:80],
        "kind": kind,
        "stage": stage,
        "value_mmk": float(value_mmk),
        "market": market,
        "owner": owner[:60],
        "event_date": event_date,          # ISO date or "" — the hard deadline
        "notes": notes[:500],
        "source": source[:40],
        "founder_confirmation_required": bool(founder_confirmation_required),
        "founder_approval": founder_approval,
        "founder_approved_by": "",
        "founder_approved_at": "",
        "created_at": _now(),
        "updated_at": _now(),
        "history": [{"at": _now(), "stage": stage, "note": "created"}],
    }
    rows = _load()
    rows.insert(0, row)
    _save(rows)
    return row


def all_projects(include_closed: bool = True) -> list[dict[str, Any]]:
    rows = _load()
    if include_closed:
        return rows
    return [r for r in rows if r.get("stage") in ACTIVE_STAGES]


def get(project_id: str) -> dict[str, Any] | None:
    for r in _load():
        if r.get("id") == project_id or r.get("slug") == project_id:
            return r
    return None


def set_stage(project_id: str, stage: str, note: str = "") -> dict[str, Any] | None:
    """Move a project along the pipeline, keeping an audit trail."""
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}")
    rows = _load()
    for r in rows:
        if r.get("id") == project_id or r.get("slug") == project_id:
            if (
                stage in {"proposal", "won", "delivery"}
                and r.get("founder_confirmation_required")
                and r.get("founder_approval") != "approved"
            ):
                raise PermissionError(
                    "founder confirmation is required before a real lead can move to proposal, won or delivery"
                )
            r["stage"] = stage
            r["updated_at"] = _now()
            r.setdefault("history", []).append(
                {"at": _now(), "stage": stage, "note": note[:200]}
            )
            _save(rows)
            return r
    return None


def confirm(
    project_id: str,
    approved_by: str,
    *,
    approve: bool = True,
    note: str = "",
) -> dict[str, Any] | None:
    """Record the founder's decision for an incoming lead or client project.

    This is the explicit gate between autonomous internal work and real-world
    agency commitments. Declined records remain in the audit trail but cannot
    move into proposal or delivery stages.
    """
    if not (approved_by or "").strip():
        raise ValueError("approved_by is required for a founder decision")
    rows = _load()
    for r in rows:
        if r.get("id") == project_id or r.get("slug") == project_id:
            decision = "approved" if approve else "declined"
            r["founder_confirmation_required"] = True
            r["founder_approval"] = decision
            r["founder_approved_by"] = approved_by.strip()[:60]
            r["founder_approved_at"] = _now()
            r["updated_at"] = _now()
            r.setdefault("history", []).append({
                "at": _now(),
                "stage": r.get("stage", "lead"),
                "note": f"founder {decision}: {note[:160]}",
            })
            _save(rows)
            return r
    return None


def update(project_id: str, **fields: Any) -> dict[str, Any] | None:
    """Edit a project in place. Unknown or protected keys are ignored."""
    editable = {"name", "client", "kind", "value_mmk", "market",
                "owner", "event_date", "notes"}
    rows = _load()
    for r in rows:
        if r.get("id") == project_id or r.get("slug") == project_id:
            for k, v in fields.items():
                if k in editable and v is not None:
                    r[k] = float(v) if k == "value_mmk" else v
            r["updated_at"] = _now()
            _save(rows)
            return r
    return None


def remove(project_id: str) -> bool:
    rows = _load()
    kept = [r for r in rows if r.get("id") != project_id and r.get("slug") != project_id]
    if len(kept) == len(rows):
        return False
    _save(kept)
    return True


def days_to(event_date: str) -> int | None:
    """Days until the project's hard date. Negative once it has passed."""
    if not event_date:
        return None
    try:
        d = date.fromisoformat(event_date[:10])
    except ValueError:
        return None
    return (d - date.today()).days


def linked_tasks(project_id: str) -> list[dict[str, Any]]:
    """Tasks whose title or notes reference this project by name or slug."""
    p = get(project_id)
    if not p:
        return []
    try:
        from utils import tasks
        rows = tasks.all_tasks()
    except Exception:
        return []
    needles = {p["slug"], p["name"].lower()}
    out = []
    for t in rows:
        blob = f"{t.get('title','')} {t.get('notes','')}".lower()
        if any(n and n in blob for n in needles) or t.get("project") == p["id"]:
            out.append(t)
    return out


def board() -> dict[str, list[dict[str, Any]]]:
    """Projects grouped by stage, for a kanban view."""
    out: dict[str, list[dict[str, Any]]] = {s: [] for s in STAGES}
    for r in _load():
        out.setdefault(r.get("stage", "lead"), []).append(r)
    return out


def summary() -> dict[str, Any]:
    """Portfolio-level numbers the MD wants at a glance."""
    rows = _load()
    active = [r for r in rows if r.get("stage") in ACTIVE_STAGES]
    weighted = {"lead": 0.1, "proposal": 0.3, "won": 0.9, "delivery": 1.0}
    pipeline = sum(r.get("value_mmk", 0) for r in active)
    expected = sum(r.get("value_mmk", 0) * weighted.get(r.get("stage"), 0) for r in active)

    upcoming = []
    for r in active:
        d = days_to(r.get("event_date", ""))
        if d is not None:
            upcoming.append({"name": r["name"], "id": r["id"], "days": d,
                             "stage": r["stage"], "date": r.get("event_date")})
    upcoming.sort(key=lambda x: x["days"])

    return {
        "total": len(rows),
        "active": len(active),
        "by_stage": {s: sum(1 for r in rows if r.get("stage") == s) for s in STAGES},
        "pipeline_mmk": pipeline,
        "expected_mmk": round(expected),
        "won_mmk": sum(r.get("value_mmk", 0) for r in rows
                       if r.get("stage") in ("won", "delivery", "done")),
        "upcoming": upcoming[:6],
    }


def seed_if_empty() -> int:
    """Put the agency's real owned project on the board so it is never empty.

    IGNITE is seeded as one row precisely to make the point that it is a
    project, not the system. Returns how many were created.
    """
    if _load():
        return 0
    add(
        "IGNITE Myanmar Business Summit 2026",
        client="ZYNTH (owned IP)",
        kind="owned",
        stage="proposal",
        value_mmk=198_000_000,
        market="MM",
        owner="MD",
        event_date="2026-11-14",
        notes="Sponsorship-funded, 300 delegates, Yangon. Inventory 198M MMK. "
              "Lean build clears the 35% floor at 43% sell-through.",
        source="seed",
    )
    return 1


def handle_api(data: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """Dispatch one ``/api/project`` request. Returns ``(payload, http_status)``.

    Lives here rather than in the HTTP handler so the dashboard's write path is
    testable without importing the Telegram stack, and so a bad request comes
    back as a clean 400 instead of a 500 traceback.
    """
    action = (data or {}).get("action")
    try:
        if action == "add":
            row = add(
                data.get("name", ""),
                client=data.get("client", ""),
                kind=data.get("kind", "event"),
                stage=data.get("stage", "lead"),
                value_mmk=float(data.get("value_mmk") or 0),
                market=data.get("market", "MM"),
                owner=data.get("owner", ""),
                event_date=data.get("event_date", ""),
                notes=data.get("notes", ""),
                source=data.get("source", "dashboard"),
            )
        elif action == "stage":
            row = set_stage(data.get("id", ""), data.get("stage", ""), data.get("note", ""))
        elif action in {"approve", "decline"}:
            row = confirm(
                data.get("id", ""),
                data.get("approved_by", "MD"),
                approve=action == "approve",
                note=data.get("note", ""),
            )
        elif action == "update":
            row = update(data.get("id", ""),
                         **{k: v for k, v in data.items() if k not in ("action", "id")})
        elif action == "remove":
            row = {"removed": True} if remove(data.get("id", "")) else None
        else:
            return {"ok": False, "error": f"unknown action {action!r}"}, 400
    except (ValueError, TypeError, PermissionError) as exc:
        return {"ok": False, "error": str(exc)}, 400

    if row is None:
        return {"ok": False, "error": "project not found"}, 404
    return {"ok": True, "project": row, "summary": summary()}, 200


__all__ = [
    "STAGES", "ACTIVE_STAGES", "KINDS", "APPROVAL_STATUSES", "add", "all_projects", "get",
    "set_stage", "confirm", "update", "remove", "board", "summary", "days_to",
    "linked_tasks", "seed_if_empty", "handle_api",
]
