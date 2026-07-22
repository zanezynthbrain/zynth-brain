"""BD outreach queue — the 1-tap-release send layer for the autonomous loop.

The AI drafts a personalised outreach email from the prospect's intelligence
(analysis, gap, ZYNTH approach) and QUEUES it. You skim on Telegram and release
with one tap — or it AUTO-RELEASES after OUTREACH_AUTO_RELEASE_HOURS if you don't
touch it. A scheduler job then sends everything that's due, respecting a daily
cap so ZYNTH's domain reputation stays healthy. You are on the loop, not in it:
you can /bd pause, /release, or /reject at any time.

Env (Railway):
  OUTREACH_AUTO_RELEASE_HOURS  default 24   (0 = never auto-release; wait for a tap)
  OUTREACH_DAILY_LIMIT         default 10   (max real emails sent per day)

Stores to outputs/proposal_pool/outreach_queue.json (committed like the rest of
the pool, so it survives redeploys).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from config import get_settings
from utils.logging_config import get_logger

logger = get_logger("outreach")

_POOL = Path("outputs/proposal_pool")
_FILE = _POOL / "outreach_queue.json"
_FMT = "%Y-%m-%d %H:%M"

# queued  → drafted, waiting for your tap or auto-release
# released→ approved to send (manually or auto)
# sent    → delivered
# rejected→ you said no
STATUSES = ("queued", "released", "sent", "rejected")


def _auto_release_hours() -> int:
    try:
        return int(os.getenv("OUTREACH_AUTO_RELEASE_HOURS", "24"))
    except ValueError:
        return 24


def _daily_limit() -> int:
    try:
        return int(os.getenv("OUTREACH_DAILY_LIMIT", "10"))
    except ValueError:
        return 10


def _load() -> list[dict]:
    if _FILE.exists():
        try:
            return json.loads(_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(rows: list[dict]) -> None:
    _POOL.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


# ── drafting ──────────────────────────────────────────────────────────────────

def draft_email(prospect: dict) -> tuple[str, str]:
    """Build a personalised, on-brand outreach email from the prospect intel.

    Template-based (deterministic, always works, no token cost) but genuinely
    personalised — it uses the company analysis, the marketing gap we spotted,
    and the tailored ZYNTH approach the researcher already produced.
    """
    s = get_settings()
    company = prospect.get("company", "your team")
    name = (prospect.get("contact_name") or "").strip()
    greeting = f"Dear {name.split()[0]}," if name else "Hello,"
    gap = (prospect.get("marketing_gap") or "").strip().rstrip(".")
    approach = (prospect.get("zynth_approach") or "").strip()
    service = (prospect.get("service_fit") or "marketing & events").strip()

    hook = f"I've been following {company}'s work"
    if gap:
        hook += f", and one thing stood out: {gap[0].lower()}{gap[1:]}."
    else:
        hook += "."

    pitch = approach or (
        f"We think there's a sharp opportunity to lift {company}'s {service} with "
        "cinematic, distinctive creative — the kind that gets remembered."
    )

    subject = f"An idea for {company}"
    body = (
        f"{greeting}\n\n"
        f"I'm Zane, founder of ZYNTH — a Singapore + Myanmar marketing and events "
        f"studio (\"The Intelligence of Creativity\").\n\n"
        f"{hook}\n\n"
        f"Here's the thinking: {pitch}\n\n"
        f"We work fast (proposals in 48 hours), price in real market terms, and hold "
        f"a cinematic standard most local teams don't. If it's worth 20 minutes, I'd "
        f"love to share a specific concept built for {company} — no obligation.\n\n"
        f"Would this week or next suit you?\n\n"
        f"Warm regards,\n"
        f"Zane\n"
        f"Founder & MD, ZYNTH\n"
        f"{s.email_to or 'zane@zynth.asia'}"
    )
    return subject, body


# ── queue operations ──────────────────────────────────────────────────────────

def already_queued(prospect_id: str) -> bool:
    pid = (prospect_id or "").strip()
    return any(q.get("prospect_id") == pid and q.get("status") != "rejected" for q in _load())


def enqueue(prospect: dict) -> dict | None:
    """Draft + queue an outreach for a prospect that has a real email. Returns the
    queue item, or None if it can't/shouldn't be queued."""
    email = (prospect.get("email") or "").strip()
    pid = prospect.get("id", "")
    if not email or not pid or already_queued(pid):
        return None
    subject, body = draft_email(prospect)
    now = datetime.now()
    hrs = _auto_release_hours()
    item = {
        "id": f"O{int(now.timestamp())}{pid[-3:]}",
        "prospect_id": pid,
        "company": prospect.get("company", ""),
        "to": email,
        "contact_name": prospect.get("contact_name", ""),
        "subject": subject,
        "body": body,
        "status": "queued",
        "queued_at": now.strftime(_FMT),
        "release_at": (now + timedelta(hours=hrs)).strftime(_FMT) if hrs > 0 else "",
    }
    rows = _load()
    rows.append(item)
    _save(rows)
    return item


def pending() -> list[dict]:
    """Items still awaiting a decision (queued)."""
    return [q for q in _load() if q.get("status") == "queued"]


def get(item_id: str) -> dict | None:
    q = (item_id or "").lower().strip()
    for it in _load():
        if it.get("id", "").lower() == q:
            return it
    return None


def _set_status(item_id: str, status: str) -> dict | None:
    rows = _load()
    q = (item_id or "").lower().strip()
    for it in rows:
        if it.get("id", "").lower() == q:
            it["status"] = status
            it[f"{status}_at"] = datetime.now().strftime(_FMT)
            _save(rows)
            return it
    return None


def release(item_id: str) -> dict | None:
    """Approve now (manual tap). It will send on the next sender tick."""
    return _set_status(item_id, "released")


def reject(item_id: str) -> dict | None:
    return _set_status(item_id, "rejected")


def _due_now() -> list[dict]:
    """Items that should be sent: explicitly released, OR queued past release_at."""
    now = datetime.now()
    due = []
    for it in _load():
        st = it.get("status")
        if st == "released":
            due.append(it)
        elif st == "queued" and it.get("release_at"):
            try:
                if datetime.strptime(it["release_at"], _FMT) <= now:
                    due.append(it)
            except ValueError:
                continue
    return due


def _sent_today() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(
        1 for it in _load()
        if it.get("status") == "sent" and (it.get("sent_at", "").startswith(today))
    )


async def send_due(paused: bool = False) -> dict:
    """Send all due items via SMTP, up to the daily cap. Returns a summary.
    Marks the prospect 'contacted' on success. No-op if paused/unconfigured."""
    from utils.mailer import has_email, send_to
    if paused or not has_email():
        return {"sent": 0, "skipped": 0, "reason": "paused" if paused else "email not configured"}

    limit = _daily_limit()
    budget = max(0, limit - _sent_today())
    if budget <= 0:
        return {"sent": 0, "skipped": len(_due_now()), "reason": f"daily cap {limit} reached"}

    sent = skipped = 0
    for it in _due_now():
        if sent >= budget:
            skipped += 1
            continue
        ok = await send_to(it["to"], it["subject"], it["body"],
                           reply_to=get_settings().email_to or "zane@zynth.asia")
        if ok:
            _set_status(it["id"], "sent")
            try:
                from utils.prospects import set_status
                set_status(it.get("prospect_id", ""), "contacted")
            except Exception:
                pass
            sent += 1
        else:
            skipped += 1
    return {"sent": sent, "skipped": skipped, "reason": ""}


def stats_text() -> str:
    rows = _load()
    by = {s: sum(1 for r in rows if r.get("status") == s) for s in STATUSES}
    return (
        f"📤 <b>Outreach queue</b>\n"
        f"Queued (awaiting you): {by['queued']}\n"
        f"Released: {by['released']} · Sent: {by['sent']} · Rejected: {by['rejected']}\n"
        f"Sent today: {_sent_today()}/{_daily_limit()} · auto-release: {_auto_release_hours()}h"
    )
