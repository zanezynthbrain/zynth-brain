"""Supplier / vendor database — structured records for BD + event sourcing.

Seed lives in backend/data/suppliers_mm.json (and _sg later). Runtime
additions go to outputs/proposal_pool/suppliers_extra.json, committed by
the daily pool workflow so they survive redeploys.

Every record: category, company, tier, best_for, rate, lead_time,
contact_person, phone, email, source, verified, notes. Rates are
benchmarks — verified:false until a human confirms via RFQ.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data"
_EXTRA = Path("outputs/proposal_pool/suppliers_extra.json")


def _load(path: Path) -> list[dict]:
    try:
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            return d.get("vendors", d) if isinstance(d, dict) else d
    except Exception:
        pass
    return []


def all_suppliers() -> list[dict]:
    seed = _load(_DATA / "suppliers_mm.json") + _load(_DATA / "suppliers_sg.json")
    return seed + _load(_EXTRA)


def categories() -> list[str]:
    return sorted({v.get("category", "?") for v in all_suppliers()})


def search(query: str = "") -> list[dict]:
    q = query.lower().strip()
    if not q:
        return all_suppliers()
    out = []
    for v in all_suppliers():
        hay = " ".join(str(v.get(k, "")) for k in ("category", "company", "best_for", "tier", "notes", "source")).lower()
        if q in hay:
            out.append(v)
    return out


def add_supplier(v: dict[str, Any]) -> None:
    extras = _load(_EXTRA)
    v.setdefault("verified", False)
    v["added_at"] = datetime.now().isoformat()
    extras.append(v)
    _EXTRA.parent.mkdir(parents=True, exist_ok=True)
    _EXTRA.write_text(json.dumps(extras, indent=2, ensure_ascii=False), encoding="utf-8")


def format_supplier(v: dict) -> str:
    flag = "✅" if v.get("verified") else "⚠️"
    lines = [
        f"{flag} <b>{v.get('company', '?')}</b>  ·  {v.get('category', '?')} ({v.get('tier', '?')})",
        f"   💡 {v.get('best_for', '')}",
        f"   💵 {v.get('rate', 'rate TBC')}  ·  ⏳ {v.get('lead_time', '?')}",
    ]
    contact = " ".join(x for x in [v.get("contact_person"), v.get("phone"), v.get("email")] if x)
    if contact:
        lines.append(f"   📞 {contact}")
    elif not v.get("verified"):
        lines.append("   📞 <i>contact not captured yet — /vendor add to fill</i>")
    return "\n".join(lines)


def stats() -> str:
    vendors = all_suppliers()
    by_cat: dict[str, int] = {}
    verified = 0
    for v in vendors:
        by_cat[v.get("category", "?")] = by_cat.get(v.get("category", "?"), 0) + 1
        if v.get("verified"):
            verified += 1
    cats = "\n".join(f"• {c}: {n}" for c, n in sorted(by_cat.items()))
    return f"{len(vendors)} suppliers, {verified} verified\n{cats}"
