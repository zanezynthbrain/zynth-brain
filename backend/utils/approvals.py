"""BD approval pipeline — tracks prospects from brief through to outreach.

The pipeline is a simple JSON file on disk:
    outputs/bd_pipeline/pipeline.json

States: pending_outreach → contacted → closed_won / closed_lost
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_PIPELINE_PATH = Path("outputs/bd_pipeline/pipeline.json")


def _load() -> dict[str, Any]:
    _PIPELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if _PIPELINE_PATH.exists():
        return json.loads(_PIPELINE_PATH.read_text())
    return {"approved": [], "skipped": []}


def _save(data: dict[str, Any]) -> None:
    _PIPELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _PIPELINE_PATH.write_text(json.dumps(data, indent=2, default=str))


def approve_prospect(prospect: dict[str, Any]) -> None:
    data = _load()
    data["approved"].append({
        **prospect,
        "approved_at": datetime.now().isoformat(),
        "status": "pending_outreach",
    })
    _save(data)


def skip_prospect(company: str) -> None:
    data = _load()
    data["skipped"].append({
        "company": company,
        "skipped_at": datetime.now().isoformat(),
    })
    _save(data)


def mark_contacted(company: str) -> bool:
    data = _load()
    for p in data["approved"]:
        if p.get("company") == company:
            p["status"] = "contacted"
            p["contacted_at"] = datetime.now().isoformat()
            _save(data)
            return True
    return False


def mark_closed(company: str, won: bool) -> bool:
    data = _load()
    for p in data["approved"]:
        if p.get("company") == company:
            p["status"] = "closed_won" if won else "closed_lost"
            p["closed_at"] = datetime.now().isoformat()
            _save(data)
            return True
    return False


def get_pending() -> list[dict[str, Any]]:
    return [p for p in _load()["approved"] if p.get("status") == "pending_outreach"]


def get_all() -> dict[str, Any]:
    return _load()


def pipeline_summary() -> str:
    data = _load()
    approved = data["approved"]
    pending = [p for p in approved if p.get("status") == "pending_outreach"]
    contacted = [p for p in approved if p.get("status") == "contacted"]
    won = [p for p in approved if p.get("status") == "closed_won"]
    skipped = len(data["skipped"])
    return (
        f"📋 BD Pipeline\n"
        f"  🟡 Pending outreach: {len(pending)}\n"
        f"  🔵 Contacted: {len(contacted)}\n"
        f"  🟢 Closed won: {len(won)}\n"
        f"  ⏭ Skipped total: {skipped}"
    )
