"""Yangon venue database — repo-versioned JSON, ephemeral-safe additions.

Sources merged at read time:
  1. backend/data/venues.json          — seed data, versioned in the repo
  2. outputs/proposal_pool/venues_extra.json — /venue add entries; this
     folder is committed back to the repo daily by the pool workflow, so
     runtime additions survive redeploys after at most one day.

Data law: every figure carries `verified`; agents must tag unverified
numbers and no rate/capacity may be quoted to a client without a fresh
confirmation from the venue.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "venues.json"
_EXTRA_PATH = Path("outputs/proposal_pool/venues_extra.json")


def _load_json(path: Path) -> list[dict]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("venues", data) if isinstance(data, dict) else data
    except Exception:
        pass
    return []


def all_venues() -> list[dict]:
    seed = _load_json(_SEED_PATH)
    extra = _load_json(_EXTRA_PATH)
    seen = {v["name"].lower() for v in seed}
    return seed + [v for v in extra if v.get("name", "").lower() not in seen]


def search(query: str = "", min_capacity: int | None = None) -> list[dict]:
    """Filter by free-text (name/type/location/notes) and/or minimum capacity."""
    q = query.lower().strip()
    results = []
    for v in all_venues():
        haystack = " ".join(
            str(v.get(k, "")) for k in ("name", "type", "location", "notes")
        ).lower()
        if q and q not in haystack:
            continue
        if min_capacity:
            caps = [c for c in (v.get("capacity") or {}).values() if c]
            if not caps or max(caps) < min_capacity:
                continue
        results.append(v)
    return results


def add_venue(venue: dict[str, Any]) -> None:
    """Append a runtime-added venue (picked up by the daily pool commit)."""
    extras = _load_json(_EXTRA_PATH)
    venue.setdefault("verified", False)
    venue.setdefault("floorplan_status", "none")
    venue["added_at"] = datetime.now().isoformat()
    extras.append(venue)
    _EXTRA_PATH.parent.mkdir(parents=True, exist_ok=True)
    _EXTRA_PATH.write_text(json.dumps(extras, indent=2, ensure_ascii=False), encoding="utf-8")


def format_venue(v: dict) -> str:
    """One venue as a Telegram-friendly card."""
    cap = v.get("capacity") or {}
    cap_txt = " · ".join(
        f"{k} {cap[k]:,}" for k in ("banquet", "theatre", "cocktail") if cap.get(k)
    ) or "capacity unknown"
    flag = "✅ verified" if v.get("verified") else "⚠️ UNVERIFIED"
    lines = [
        f"<b>{v.get('name')}</b> ({v.get('type', '?')}) — {flag}",
        f"📍 {v.get('location', '?')}",
        f"👥 {cap_txt}",
    ]
    if v.get("sqm"):
        lines.append(f"📐 {v['sqm']:,} sqm")
    if v.get("phone") or v.get("email"):
        lines.append(f"📞 {v.get('phone') or ''} {v.get('email') or ''}".strip())
    lines.append(f"🗂 Floor plan: {v.get('floorplan_status', 'none')}")
    if v.get("notes"):
        lines.append(f"📝 {v['notes'][:150]}")
    return "\n".join(lines)


def venues_block(max_chars: int = 2500) -> str:
    """Compact venue table for proposal-writing prompts."""
    rows = []
    for v in all_venues():
        cap = v.get("capacity") or {}
        cap_txt = "/".join(str(cap.get(k) or "?") for k in ("banquet", "theatre", "cocktail"))
        flag = "" if v.get("verified") else " [UNVERIFIED]"
        rows.append(f"- {v['name']} ({v.get('type','?')}): bqt/thr/ckt {cap_txt}{flag}")
    block = (
        "\n\nYANGON VENUE DATABASE (capacities banquet/theatre/cocktail; "
        "UNVERIFIED figures must be tagged 'to be confirmed with venue' in "
        "any client document):\n" + "\n".join(rows)
    )
    return block[:max_chars]


OUTREACH_EMAIL_TEMPLATE = """Subject: Event kit & floor plans request — ZYNTH Asia (upcoming corporate events pipeline)

Dear {venue} Events Team,

I am Zane, Managing Director of ZYNTH Asia (www.zynth.asia), a marketing and
events agency serving corporate clients in Myanmar and Singapore. We are
currently planning several corporate events for the coming season, including
a flagship business summit in November 2026, and {venue} is on our shortlist.

Could you kindly share:
1. Your latest event kit / banquet brochure with 2026 pricing
2. Floor plans (PDF/CAD) for your function spaces, with capacities by setup
   (banquet / theatre / cocktail) and ceiling heights
3. In-house AV capabilities and policy on external production vendors
4. Available dates and provisional-hold policy for Q4 2026

We place multiple events per year and are looking to establish preferred
venue partners. I would also welcome a short site visit at your convenience.

Best regards,
Zane
Managing Director, ZYNTH Asia
zane@zynth.asia | www.zynth.asia
"""


def outreach_email(venue_name: str) -> str:
    return OUTREACH_EMAIL_TEMPLATE.format(venue=venue_name)
