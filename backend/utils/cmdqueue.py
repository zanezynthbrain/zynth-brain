"""Command queue — lets the web dashboard trigger the bot's real work.

The dashboard's Command Deck POSTs a whitelisted command to /api/cmd, which
enqueues it here. A scheduler drain job (every minute) runs the matching async
function and reports the result to Telegram. Browser buttons therefore trigger
real agency work — safely, because only the whitelist can ever run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

_FILE = Path("outputs/proposal_pool/cmd_queue.json")

# name → human label. The scheduler maps these to real functions.
ALLOWED = {
    "brief": "Daily CEO Brief",
    "research": "Scout Prospects",
    "autopilot": "Run BD Autopilot",
    "consolidation": "Nightly Consolidation",
    "costaudit": "Cost Audit",
    "proposals": "Generate Proposals",
    "push": "Sync to GitHub/Obsidian",
    "improve": "Self-Improvement Review",
}


def _load() -> list[dict]:
    if _FILE.exists():
        try:
            return json.loads(_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(rows: list[dict]) -> None:
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def enqueue(cmd: str) -> bool:
    """Queue a whitelisted command. Returns False if unknown or already pending."""
    if cmd not in ALLOWED:
        return False
    rows = _load()
    if any(r.get("cmd") == cmd and r.get("status") == "pending" for r in rows):
        return True  # already queued — idempotent
    rows.append({"cmd": cmd, "status": "pending", "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    _save(rows)
    return True


def take_pending() -> list[str]:
    """Return pending command names and mark them running (drained by the job)."""
    rows = _load()
    pending = [r for r in rows if r.get("status") == "pending"]
    for r in pending:
        r["status"] = "done"
        r["ran_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if pending:
        # keep only the last 30 entries
        _save(rows[-30:])
    return [r["cmd"] for r in pending]
