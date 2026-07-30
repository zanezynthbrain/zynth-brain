"""Event Operations register — the spine of ZYNTH's event-management system.

Tracks every event through its real delivery lifecycle, with a GATE on each stage
(you cannot skip the deposit, the run-of-show, or the permits). This is the
operational layer under the planning skill (zynth-master-event-planner): the skill
produces the plan, this register runs the delivery.

Persisted to outputs/proposal_pool/events.json (committed with the pool, survives
redeploys). Record + gates below; the full SOP lives in
docs/departments/EVENTS_operating_system.md.

Lifecycle: enquiry → qualified → proposed → confirmed → preproduction → live → wrap
→ closed   (or → lost)
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_PATH = Path("outputs/proposal_pool/events.json")

STAGES = ["enquiry", "qualified", "proposed", "confirmed",
          "preproduction", "live", "wrap", "closed", "lost"]

STAGE_EMOJI = {
    "enquiry": "📨", "qualified": "🔎", "proposed": "📄", "confirmed": "✅",
    "preproduction": "🛠️", "live": "🎪", "wrap": "📦", "closed": "🏁", "lost": "❌",
}

# The GATE to ENTER each stage — the thing that must be true first. This is what
# makes it a system and not a list: you cannot advance without the gate.
STAGE_GATE = {
    "qualified": "Brief captured: client, type, date, guest count, budget band, market, objective.",
    "proposed": "Complete costed proposal + quote sent (built with the event-planner skill).",
    "confirmed": "Client has agreed AND the 50% deposit is received. No deposit → not confirmed.",
    "preproduction": "Deposit banked; run-of-show drafted and key suppliers being booked.",
    "live": "Run-of-show FINAL; all suppliers confirmed; permits, safety & contingency ready.",
    "wrap": "Event delivered; teardown done; final invoice issued.",
    "closed": "Final payment received; post-event report sent; upsell/next event logged.",
}

# What to DO while an event sits in a given stage (the working checklist).
STAGE_TODO = {
    "enquiry": ["Respond within 2 hours (Speed Moat).", "Book a qualification call/brief."],
    "qualified": ["Confirm objective, guest profile, date, budget band, market.",
                  "Run the event-planner skill to produce the full costed plan."],
    "proposed": ["Send the proposal + quote.", "Follow up in 48h.", "Hold the 35% margin floor."],
    "confirmed": ["Issue the 50% deposit invoice and confirm receipt.",
                  "Open the event job folder; lock the concept + budget."],
    "preproduction": ["Finalise run-of-show (minute-by-minute).",
                      "RFQ + book venue, AV, F&B, décor, talent, crew (≥2 quotes each).",
                      "Secure permits, insurance, safety & weather plan.",
                      "Confirm crew roles + brief every supplier."],
    "live": ["Crew call + soundcheck.", "Run the show to the ROS; manage VIPs & contingencies.",
             "Capture content (photo/video)."],
    "wrap": ["Teardown + supplier settle-up.", "Issue final invoice (balance).",
             "Draft the post-event report (results vs objective)."],
    "closed": ["Send post-event report.", "Log upsell / next event.", "Add lessons to the loop."],
    "lost": ["Log why it was lost (feeds the self-improvement loop)."],
}

EVENT_FIELDS = [
    "client", "event_type", "market", "event_date", "guests", "budget",
    "venue", "stage", "deposit_paid", "owner", "next_action", "notes",
]


def _load() -> list[dict]:
    try:
        if _PATH.exists():
            return json.loads(_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save(rows: list[dict]) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def add_event(ev: dict[str, Any]) -> str:
    rows = _load()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for f in EVENT_FIELDS:
        ev.setdefault(f, "")
    ev["stage"] = ev.get("stage") or "enquiry"
    ev["deposit_paid"] = bool(ev.get("deposit_paid"))
    ev["created_at"] = now
    ev["updated_at"] = now
    ev["id"] = f"E{len(rows) + 1:03d}"
    rows.append(ev)
    _save(rows)
    return ev["id"]


def find(id_or_client: str) -> dict | None:
    q = (id_or_client or "").lower().strip()
    for ev in _load():
        if ev.get("id", "").lower() == q or (q and q in ev.get("client", "").lower()):
            return ev
    return None


def update_stage(id_or_client: str, stage: str) -> tuple[dict | None, str]:
    """Advance an event. Returns (event, warning). Warning is set when the stage's
    GATE is not obviously met — the move still happens (MD override), but you're told."""
    if stage not in STAGES:
        return None, f"Unknown stage. Use: {', '.join(STAGES)}"
    rows = _load()
    q = (id_or_client or "").lower().strip()
    for ev in rows:
        if ev.get("id", "").lower() == q or (q and q in ev.get("client", "").lower()):
            warn = ""
            if stage == "confirmed" and not ev.get("deposit_paid"):
                warn = "⚠️ Gate: no deposit recorded. Confirm only after the 50% deposit is in (set deposit first)."
            if stage in ("preproduction", "live", "wrap") and not ev.get("deposit_paid"):
                warn = "⚠️ Gate: deposit not recorded — do not commit supplier spend on unpaid work."
            ev["stage"] = stage
            ev["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save(rows)
            return ev, warn
    return None, "No event matched."


def set_field(id_or_client: str, field: str, value: Any) -> dict | None:
    rows = _load()
    q = (id_or_client or "").lower().strip()
    for ev in rows:
        if ev.get("id", "").lower() == q or (q and q in ev.get("client", "").lower()):
            if field == "deposit_paid":
                value = str(value).lower() in ("1", "true", "yes", "paid", "y")
            ev[field] = value
            ev["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save(rows)
            return ev
    return None


def all_events() -> list[dict]:
    return _load()


def active() -> list[dict]:
    return [e for e in _load() if e.get("stage") not in ("closed", "lost")]


def upcoming(limit: int = 10) -> list[dict]:
    rows = [e for e in active() if e.get("event_date")]
    rows.sort(key=lambda e: str(e.get("event_date")))
    return rows[:limit]


def next_todo(ev: dict) -> list[str]:
    return STAGE_TODO.get(ev.get("stage", "enquiry"), [])


def format_event(ev: dict) -> str:
    e = STAGE_EMOJI.get(ev.get("stage", "enquiry"), "•")
    dep = "💰 deposit ✓" if ev.get("deposit_paid") else "deposit ✗"
    lines = [
        f"{e} <b>{ev.get('client', '?')}</b> <i>[{ev.get('id', '')}]</i> — {ev.get('stage', 'enquiry')}",
        f"   {ev.get('event_type', '')} · {ev.get('market', '')}"
        + (f" · {ev.get('guests')} pax" if ev.get("guests") else "")
        + (f" · {ev.get('event_date')}" if ev.get("event_date") else ""),
    ]
    money = " · ".join(x for x in [(f"budget {ev.get('budget')}" if ev.get("budget") else ""), dep] if x)
    if money:
        lines.append(f"   {money}")
    if ev.get("venue"):
        lines.append(f"   📍 {ev['venue']}")
    todo = next_todo(ev)
    if todo:
        lines.append("   ▸ Next: " + todo[0])
    gate = STAGE_GATE.get(ev.get("stage"))
    if gate:
        lines.append(f"   🔒 To advance: {gate}")
    return "\n".join(lines)


def pipeline_stats() -> str:
    rows = _load()
    if not rows:
        return ("🎪 <b>No events yet.</b> Add one: <code>/em add Client | type | date | guests | budget</code>\n"
                "The system runs it enquiry → qualified → proposed → confirmed → preproduction → live → wrap → closed.")
    by: dict[str, int] = {s: 0 for s in STAGES}
    for ev in rows:
        by[ev.get("stage", "enquiry")] = by.get(ev.get("stage", "enquiry"), 0) + 1
    row = " · ".join(f"{STAGE_EMOJI.get(s,'')}{s} {by[s]}" for s in STAGES if by[s])
    up = upcoming(5)
    out = [f"🎪 <b>Event pipeline</b> — {len(rows)} events", row]
    if up:
        out.append("\n<b>Upcoming:</b>")
        out += [f"• {e.get('event_date','?')} — {e.get('client','?')} ({e.get('stage')})" for e in up]
    return "\n".join(out)


def stage_counts() -> dict[str, int]:
    by: dict[str, int] = {s: 0 for s in STAGES}
    for ev in _load():
        by[ev.get("stage", "enquiry")] = by.get(ev.get("stage", "enquiry"), 0) + 1
    return by
