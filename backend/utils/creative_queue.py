"""Creative production queue — the bridge between the 24/7 bot and real generation.

The problem this solves
-----------------------
The Railway bot can produce *text* around the clock, cheaply. It cannot produce
media: OpenArt / Higgsfield / Blender are MCP + local tools that only exist
inside a live Claude Code session. A cron job can never generate a video.

So we split the work in two:

1. **Prep (autonomous, 24/7, cheap).** Scheduled jobs write fully-formed
   generation *jobs* here — a video brief with its shot prompts, a design spec
   with its render prompt, a 3D scene spec. Text only, no credits spent.
2. **Drain (live session, costs credits).** In a Claude Code session the MD says
   "drain the creative queue" and every pending item is generated in one batch,
   with the MD seeing the cost before it is spent.

The queue is JSON under ``outputs/proposal_pool/`` so it rides the same
git-as-database path as the proposal pool, and survives Railway redeploys.

Nothing here spends money. This module only ever reads and writes JSON.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

_FILE = Path("outputs/proposal_pool/creative_queue.json")

#: What a queued item can ask for. Each maps to a real tool in a live session.
KINDS = {
    "image": "Still image — key visual, poster, social, storyboard frame",
    "video": "AI-generated video clip (OpenArt / Higgsfield)",
    "scene3d": "3D event/stage scene built headlessly in Blender (bpy)",
}

#: Lifecycle. Items only ever move forward.
STATUSES = ("pending", "generated", "failed", "skipped")

_MAX_KEPT = 300  # trim oldest done items beyond this so the file stays small


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load() -> list[dict[str, Any]]:
    if not _FILE.exists():
        return []
    try:
        data = json.loads(_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _save(items: list[dict[str, Any]]) -> None:
    # Keep every pending item; trim only the oldest finished ones.
    pending = [i for i in items if i.get("status") == "pending"]
    done = [i for i in items if i.get("status") != "pending"]
    if len(done) > _MAX_KEPT:
        done = sorted(done, key=lambda i: i.get("queued_at", ""))[-_MAX_KEPT:]
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(
        json.dumps(pending + done, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def add(
    kind: str,
    brand: str,
    title: str,
    prompt: str,
    *,
    notes: str = "",
    spec: dict[str, Any] | None = None,
    source: str = "scheduler",
) -> dict[str, Any]:
    """Queue one generation job. Returns the stored item.

    ``prompt`` is the thing a generation model will actually receive, so it must
    be complete on its own — the draining session should not have to reconstruct
    context. ``spec`` carries structured extras (duration, aspect, model hint).
    """
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind!r}; expected one of {sorted(KINDS)}")
    if not prompt.strip():
        raise ValueError("prompt is required — a queued job must be generatable as-is")

    item = {
        "id": uuid.uuid4().hex[:12],
        "kind": kind,
        "brand": brand,
        "title": title,
        "prompt": prompt.strip(),
        "notes": notes,
        "spec": spec or {},
        "status": "pending",
        "source": source,
        "queued_at": _now(),
        "resolved_at": None,
        "result": None,
    }
    items = _load()
    items.insert(0, item)
    _save(items)
    return item


def pending(kind: str | None = None, brand: str | None = None) -> list[dict[str, Any]]:
    """Everything still waiting to be generated, newest first."""
    out = [i for i in _load() if i.get("status") == "pending"]
    if kind:
        out = [i for i in out if i.get("kind") == kind]
    if brand:
        out = [i for i in out if (i.get("brand") or "").lower() == brand.lower()]
    return out


def resolve(item_id: str, status: str, result: str = "") -> bool:
    """Mark a queued job done. ``result`` is the URL or file path produced."""
    if status not in STATUSES or status == "pending":
        raise ValueError(f"status must be one of {STATUSES[1:]}")
    items = _load()
    for i in items:
        if i.get("id") == item_id:
            i["status"] = status
            i["result"] = result
            i["resolved_at"] = _now()
            _save(items)
            return True
    return False


def counts() -> dict[str, int]:
    """Queue depth by kind, plus totals — what the dashboard and /queue show."""
    items = _load()
    p = [i for i in items if i.get("status") == "pending"]
    out = {k: sum(1 for i in p if i.get("kind") == k) for k in KINDS}
    out["pending"] = len(p)
    out["generated"] = sum(1 for i in items if i.get("status") == "generated")
    return out


def summary_lines(limit: int = 10) -> list[str]:
    """Human-readable pending list for Telegram / the dashboard."""
    rows = pending()[:limit]
    if not rows:
        return ["Creative queue is empty."]
    lines = []
    for i in rows:
        lines.append(f"[{i['kind']}] {i['brand']} — {i['title']}  ({i['id']})")
    extra = len(pending()) - len(rows)
    if extra > 0:
        lines.append(f"…and {extra} more")
    return lines


def export_for_session(kinds: Iterable[str] | None = None) -> str:
    """A copy-paste block a live Claude Code session can act on directly.

    Deliberately plain text: the draining session reads this, generates each
    prompt with the right tool, then calls ``resolve()`` per id.
    """
    want = set(kinds) if kinds else set(KINDS)
    rows = [i for i in pending() if i["kind"] in want]
    if not rows:
        return "Creative queue is empty — nothing to generate."
    parts = [f"{len(rows)} pending generation job(s):", ""]
    for i in rows:
        parts.append(f"--- id={i['id']}  kind={i['kind']}  brand={i['brand']}")
        parts.append(f"title : {i['title']}")
        if i.get("spec"):
            parts.append(f"spec  : {json.dumps(i['spec'], ensure_ascii=False)}")
        if i.get("notes"):
            parts.append(f"notes : {i['notes']}")
        parts.append(f"prompt: {i['prompt']}")
        parts.append("")
    return "\n".join(parts)


__all__ = [
    "KINDS", "STATUSES", "add", "pending", "resolve",
    "counts", "summary_lines", "export_for_session",
]
