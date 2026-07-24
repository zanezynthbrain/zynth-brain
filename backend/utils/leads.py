"""Client leads / BD pipeline database — collect data day by day.

Persisted to outputs/proposal_pool/leads.json (committed by the daily pool
workflow, survives redeploys). This is the BD data the MD asked for: real
records, not a format.

Record: company, contact_person, phone, email, industry, market, source,
stage, value_sgd, next_step, notes, created_at, updated_at.

Stages: new → contacted → meeting → proposal → won / lost
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_PATH = Path("outputs/proposal_pool/leads.json")

STAGES = ["new", "contacted", "meeting", "proposal", "won", "lost"]


def _load() -> list[dict]:
    try:
        if _PATH.exists():
            return json.loads(_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save(leads: list[dict]) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(json.dumps(leads, indent=2, ensure_ascii=False), encoding="utf-8")


# Full BD-spine record schema. Missing fields default to "" so every lead has
# the same shape (company, sector, channels, ads observed, contact, pipeline).
LEAD_FIELDS = [
    "company", "sector", "website", "facebook", "tiktok", "linkedin",
    "ads_observed", "contact_person", "contact_title", "email", "phone",
    "contact_linkedin", "source", "stage", "next_action", "value", "notes",
]


def add_lead(lead: dict[str, Any]) -> str:
    leads = _load()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for f in LEAD_FIELDS:
        lead.setdefault(f, "")
    lead["stage"] = lead.get("stage") or "new"
    lead["created_at"] = now
    lead["updated_at"] = now
    lead["id"] = f"L{len(leads) + 1:03d}"
    leads.append(lead)
    _save(leads)
    return lead["id"]


def update_stage(company_or_id: str, stage: str) -> dict | None:
    if stage not in STAGES:
        return None
    leads = _load()
    q = company_or_id.lower()
    for lead in leads:
        if lead.get("id", "").lower() == q or q in lead.get("company", "").lower():
            lead["stage"] = stage
            lead["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save(leads)
            return lead
    return None


def all_leads() -> list[dict]:
    return _load()


def search(query: str = "", stage: str | None = None) -> list[dict]:
    q = query.lower().strip()
    out = []
    for lead in _load():
        if stage and lead.get("stage") != stage:
            continue
        if q:
            hay = " ".join(str(lead.get(k, "")) for k in ("company", "contact_person", "industry", "notes", "source")).lower()
            if q not in hay:
                continue
        out.append(lead)
    return out


def format_lead(lead: dict) -> str:
    stage_emoji = {"new": "🆕", "contacted": "📞", "meeting": "🤝", "proposal": "📄", "won": "✅", "lost": "❌"}
    e = stage_emoji.get(lead.get("stage", "new"), "•")
    lines = [
        f"{e} <b>{lead.get('company', '?')}</b> <i>[{lead.get('id', '')}]</i> — {lead.get('stage', 'new')}",
        f"   {lead.get('industry', '')} · {lead.get('market', '')}",
    ]
    contact = " ".join(x for x in [lead.get("contact_person"), lead.get("phone"), lead.get("email")] if x)
    if contact:
        lines.append(f"   📞 {contact}")
    if lead.get("value_sgd"):
        lines.append(f"   💰 ~S${lead['value_sgd']}")
    if lead.get("next_step"):
        lines.append(f"   ➡️ {lead['next_step']}")
    return "\n".join(lines)


def pipeline_stats() -> str:
    leads = _load()
    if not leads:
        return "No leads yet. Add your first with /lead add."
    by_stage: dict[str, int] = {s: 0 for s in STAGES}
    value = 0.0
    for lead in leads:
        by_stage[lead.get("stage", "new")] = by_stage.get(lead.get("stage", "new"), 0) + 1
        if lead.get("stage") not in ("won", "lost"):
            try:
                value += float(lead.get("value_sgd", 0) or 0)
            except Exception:
                pass
    row = " · ".join(f"{s} {by_stage[s]}" for s in STAGES if by_stage[s])
    return f"📊 <b>Pipeline:</b> {len(leads)} leads\n{row}\n💰 Open value: ~S${value:,.0f}"
