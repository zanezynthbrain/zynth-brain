"""Task & activity system — the productivity layer behind the dashboard.

Two stores, both in outputs/proposal_pool/ (committed by the daily pool
workflow, so they survive redeploys):
  - tasks.json     : work items with department, status, assignee
  - activity.json  : a rolling feed of everything that happens (lead added,
                     proposal generated, note filed, task moved…) so the
                     dashboard reflects what hit Telegram/Gmail.

Both the Telegram bot and the dashboard read/write here — one source of truth.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_TASKS = Path("outputs/proposal_pool/tasks.json")
_ACTIVITY = Path("outputs/proposal_pool/activity.json")

DEPARTMENTS = ["BD", "Events", "Creative", "Marketing", "Operations", "Finance", "Content"]
STATUSES = ["todo", "doing", "done"]

_DEPT_ALIASES = {
    "sales": "BD", "bd": "BD", "biz": "BD", "leads": "BD",
    "event": "Events", "events": "Events",
    "creative": "Creative", "design": "Creative",
    "marketing": "Marketing", "ads": "Marketing", "seo": "Marketing",
    "ops": "Operations", "operations": "Operations",
    "finance": "Finance", "money": "Finance",
    "content": "Content", "social": "Content",
}


def normalize_dept(text: str) -> str:
    t = (text or "").strip().lower()
    if t in _DEPT_ALIASES:
        return _DEPT_ALIASES[t]
    for d in DEPARTMENTS:
        if d.lower() == t:
            return d
    return "Operations"


# ── tasks ─────────────────────────────────────────────────────────────────────

def _load_tasks() -> list[dict]:
    try:
        if _TASKS.exists():
            return json.loads(_TASKS.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save_tasks(tasks: list[dict]) -> None:
    _TASKS.parent.mkdir(parents=True, exist_ok=True)
    _TASKS.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


def all_tasks() -> list[dict]:
    return _load_tasks()


def add_task(title: str, department: str = "Operations", assignee: str = "", notes: str = "", source: str = "bot") -> dict:
    tasks = _load_tasks()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    task = {
        "id": f"T{len(tasks) + 1:03d}",
        "title": title.strip(),
        "department": normalize_dept(department),
        "status": "todo",
        "assignee": assignee.strip(),
        "notes": notes.strip(),
        "created_at": now,
        "updated_at": now,
    }
    tasks.append(task)
    _save_tasks(tasks)
    log_activity(task["department"], f"Task added: {task['title']}", source=source)
    return task


def set_status(task_id: str, status: str) -> dict | None:
    if status not in STATUSES:
        return None
    tasks = _load_tasks()
    q = task_id.strip().lower()
    for t in tasks:
        if t["id"].lower() == q or q in t["title"].lower():
            t["status"] = status
            t["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save_tasks(tasks)
            log_activity(t["department"], f"Task → {status}: {t['title']}")
            return t
    return None


def assign_task(task_id: str, assignee: str) -> dict | None:
    tasks = _load_tasks()
    q = task_id.strip().lower()
    for t in tasks:
        if t["id"].lower() == q or q in t["title"].lower():
            t["assignee"] = assignee.strip()
            t["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save_tasks(tasks)
            log_activity(t["department"], f"Assigned to {assignee}: {t['title']}")
            return t
    return None


def tasks_by_department() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {d: [] for d in DEPARTMENTS}
    for t in _load_tasks():
        out.setdefault(t.get("department", "Operations"), []).append(t)
    return out


# ── activity feed ─────────────────────────────────────────────────────────────

def _load_activity() -> list[dict]:
    try:
        if _ACTIVITY.exists():
            return json.loads(_ACTIVITY.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def log_activity(department: str, text: str, source: str = "bot") -> None:
    """Append an event to the rolling feed (kept to the last 200)."""
    try:
        feed = _load_activity()
        feed.append({
            "at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "department": normalize_dept(department),
            "text": text[:200],
            "source": source,
        })
        feed = feed[-200:]
        _ACTIVITY.parent.mkdir(parents=True, exist_ok=True)
        _ACTIVITY.write_text(json.dumps(feed, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass  # activity logging must never break a command


def recent_activity(limit: int = 30, department: str | None = None) -> list[dict]:
    feed = list(reversed(_load_activity()))
    if department:
        feed = [a for a in feed if a.get("department") == department]
    return feed[:limit]
