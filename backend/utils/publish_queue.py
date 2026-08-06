"""Publishing queue — the gate between a content plan and a live Meta page.

Every post the studio produces enters here as ``pending``. Nothing reaches
Facebook or Instagram until the MD approves that specific entry in Telegram.
This is the standing rule ("nothing sends externally without MD confirmation")
expressed as a state machine:

    pending ──approve──▶ approved ──schedule──▶ scheduled ──(IG only)──▶ published
       └────skip────▶ skipped                      └──────failed◀── error

Facebook entries reach ``scheduled`` and Meta takes over — the bot can go down
and the post still publishes. Instagram entries stay ``approved`` with a
``publish_at`` and are fired by the scheduler at that minute, because Instagram
has no scheduling API.

Persisted to outputs/proposal_pool/publish_queue.json so the queue survives a
redeploy — a scheduled month must not evaporate when Railway restarts.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from utils.logging_config import get_logger

logger = get_logger("utils.publish_queue")

_FILE = Path("outputs/proposal_pool/publish_queue.json")

STATES = ("pending", "approved", "scheduled", "published", "skipped", "failed")

#: Yangon is UTC+6:30; the scheduler and every displayed time use it.
YANGON = timezone(timedelta(hours=6, minutes=30))


def _load() -> list[dict]:
    try:
        if _FILE.exists():
            data = json.loads(_FILE.read_text(encoding="utf-8"))
            return data.get("queue", data) if isinstance(data, dict) else data
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not read publish queue: %s", exc)
    return []


def _save(queue: list[dict]) -> None:
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")


def all_entries() -> list[dict]:
    return _load()


def get(entry_id: str) -> dict | None:
    return next((e for e in _load() if e.get("id") == entry_id), None)


def by_state(state: str) -> list[dict]:
    return [e for e in _load() if e.get("state") == state]


def _slot_times(plan: dict[str, Any], start: datetime) -> dict[int, datetime]:
    """Default posting times per week, Yangon evenings — overridable per entry."""
    return {week: start + timedelta(days=7 * (week - 1)) for week in (1, 2, 3, 4)}


def enqueue_plan(plan: dict[str, Any], start: datetime, brand: str = "") -> list[dict]:
    """Load a content plan into the queue as pending entries, one per post.

    ``start`` is when week 1 begins (timezone-aware). Each post is spaced within
    its week so a 16-post month lands roughly every other day rather than in a
    burst. Nothing here talks to Meta.
    """
    if start.tzinfo is None:
        raise ValueError("start must be timezone-aware (use Asia/Rangoon).")

    content = plan.get("content", {}) or {}
    posts = content.get("posts", []) or []
    brand = brand or plan.get("brand", "") or "ZYNTH"
    month = plan.get("month", "")
    queue = _load()
    existing = {e.get("id") for e in queue}
    week_start = _slot_times(plan, start)

    added: list[dict] = []
    per_week: dict[int, int] = {}
    for post in posts:
        ref = post.get("ref", "")
        entry_id = f"{brand}-{month}-{ref}".replace(" ", "").lower()
        if entry_id in existing:
            continue
        week = int(post.get("week", 1) or 1)
        index = per_week.get(week, 0)
        per_week[week] = index + 1
        # Spread within the week: every other day, 19:00 Yangon.
        when = week_start.get(week, start) + timedelta(days=min(6, index * 2))
        when = when.replace(hour=19, minute=0, second=0, microsecond=0)

        entry = {
            "id": entry_id,
            "brand": brand,
            "month": month,
            "ref": ref,
            "platform": post.get("platform", ""),
            "content_type": post.get("content_type", ""),
            "caption_en": post.get("caption_en", ""),
            "caption_mm": post.get("caption_mm", ""),
            "hook_mm": post.get("hook_mm", ""),
            "hashtags": post.get("hashtags", []) or [],
            "cta": post.get("cta", ""),
            "needs_design": bool(post.get("needs_design")),
            "asset_path": "",
            "asset_url": "",
            "publish_at": when.isoformat(),
            "state": "pending",
            "meta_post_id": "",
            "error": "",
            "history": [{"at": datetime.now(YANGON).isoformat(), "event": "queued"}],
        }
        queue.append(entry)
        added.append(entry)

    _save(queue)
    logger.info("Queued %d post(s) for %s %s", len(added), brand, month)
    return added


def _update(entry_id: str, **changes: Any) -> dict | None:
    queue = _load()
    for i, entry in enumerate(queue):
        if entry.get("id") != entry_id:
            continue
        event = changes.pop("_event", None)
        entry.update(changes)
        if event:
            entry.setdefault("history", []).append(
                {"at": datetime.now(YANGON).isoformat(), "event": event}
            )
        queue[i] = entry
        _save(queue)
        return entry
    return None


def approve(entry_id: str) -> dict | None:
    """MD approves this specific post. Required before anything can be sent."""
    return _update(entry_id, state="approved", _event="approved by MD")


def skip(entry_id: str, reason: str = "") -> dict | None:
    return _update(entry_id, state="skipped", error=reason, _event=f"skipped{': ' + reason if reason else ''}")


def mark_scheduled(entry_id: str, post_id: str, when: str) -> dict | None:
    return _update(entry_id, state="scheduled", meta_post_id=post_id, publish_at=when,
                   _event=f"scheduled on Meta ({post_id})")


def mark_published(entry_id: str, post_id: str) -> dict | None:
    return _update(entry_id, state="published", meta_post_id=post_id, _event="published")


def mark_failed(entry_id: str, error: str) -> dict | None:
    return _update(entry_id, state="failed", error=error, _event=f"failed: {error[:120]}")


def set_asset(entry_id: str, path: str, url: str = "") -> dict | None:
    return _update(entry_id, asset_path=path, asset_url=url, _event="asset attached")


def reschedule(entry_id: str, when: datetime) -> dict | None:
    if when.tzinfo is None:
        raise ValueError("when must be timezone-aware.")
    return _update(entry_id, publish_at=when.isoformat(), _event=f"rescheduled to {when.isoformat()}")


def due_instagram(now: datetime | None = None, window_minutes: int = 15) -> list[dict]:
    """Approved Instagram entries whose publish time has arrived.

    Instagram can't be scheduled at Meta, so the scheduler asks this every few
    minutes and fires what's due. The window catches entries missed during a
    restart instead of silently dropping them.
    """
    now = now or datetime.now(YANGON)
    due = []
    for entry in _load():
        if entry.get("state") != "approved":
            continue
        from utils.meta import platform_of
        if platform_of(entry.get("platform", "")) != "instagram":
            continue
        try:
            when = datetime.fromisoformat(entry["publish_at"])
        except Exception:  # noqa: BLE001
            continue
        if when.tzinfo is None:
            when = when.replace(tzinfo=YANGON)
        if when <= now <= when + timedelta(minutes=window_minutes) or when <= now:
            due.append(entry)
    return due


def stats() -> dict[str, int]:
    counts = {state: 0 for state in STATES}
    for entry in _load():
        state = entry.get("state", "pending")
        counts[state] = counts.get(state, 0) + 1
    return counts


def summary_text() -> str:
    counts = stats()
    if not any(counts.values()):
        return "Publishing queue is empty. Load a month with /schedule <brand>."
    parts = [f"{state}: {n}" for state, n in counts.items() if n]
    return " · ".join(parts)


def clear_state(state: str) -> int:
    """Drop entries in one state (housekeeping for skipped/failed)."""
    queue = _load()
    keep = [e for e in queue if e.get("state") != state]
    removed = len(queue) - len(keep)
    _save(keep)
    return removed


__all__ = [
    "STATES", "YANGON", "all_entries", "get", "by_state", "enqueue_plan",
    "approve", "skip", "mark_scheduled", "mark_published", "mark_failed",
    "set_asset", "reschedule", "due_instagram", "stats", "summary_text", "clear_state",
]
