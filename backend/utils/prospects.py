"""Myanmar business prospect database — the market researcher's memory.

This is the raw TARGET pool: potential businesses ZYNTH could win as clients,
collected day by day by the Market Researcher agent (and seeded with known
Myanmar companies). A prospect graduates into utils/leads.py once you actually
start working it (contacted → meeting → proposal).

Store: outputs/proposal_pool/prospects.json (committed by the daily pool
workflow, so it survives Railway redeploys — the repo is the durable DB).

Record:
  id, company, industry, sub_sector, location, size, why_fit, fit_score(1-5),
  service_fit (which ZYNTH service), website, facebook, phone, email,
  source, status, verified, created_at.

Status: new → reviewing → contacted → qualified → dropped
(Only 'contacted'+ should also exist as a lead in leads.py.)

Design rule (matches the rest of ZYNTH): NEVER invent a phone/email. Unknown
contact fields stay "" and the record is marked verified:false — verification
is human work. Quality over volume: a deduped, fit-scored target beats a
scraped list of noise.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

_PATH = Path("outputs/proposal_pool/prospects.json")
_SEED = Path(__file__).resolve().parent.parent / "data" / "prospects_seed.json"

STATUSES = ["new", "reviewing", "contacted", "qualified", "dropped"]

# ZYNTH's target industries in the Myanmar market (drives daily rotation).
TARGET_SECTORS = [
    "Banking & Fintech",
    "Telecom & Technology",
    "FMCG & Consumer Goods",
    "Retail & Shopping Malls",
    "Real Estate & Property",
    "Food & Beverage / Restaurant chains",
    "Healthcare & Pharma",
    "Education & EdTech",
    "Automotive & Distribution",
    "Hospitality, Hotels & Travel",
    "Insurance & Financial Services",
    "Manufacturing & Industrial",
    "Construction & Engineering",
    "Beauty, Fashion & Lifestyle",
    "Logistics & E-commerce",
    "Energy, Oil & Gas",
    "Agriculture & Agribusiness",
    "NGO, Development & Government",
]

_SUFFIXES = re.compile(
    r"\b(co\.?,?\s*ltd\.?|company limited|limited|ltd\.?|pcl|plc|group|holdings?|"
    r"public company|private|pte\.?|llc|inc\.?|corp\.?|corporation|myanmar|mm)\b",
    re.IGNORECASE,
)


def _norm(name: str) -> str:
    """Normalise a company name for dedupe (drop legal suffixes/punctuation)."""
    n = (name or "").lower()
    n = _SUFFIXES.sub(" ", n)
    n = re.sub(r"[^a-z0-9က-႟]+", " ", n)  # keep latin + Myanmar unicode
    return re.sub(r"\s+", " ", n).strip()


# ── storage ───────────────────────────────────────────────────────────────────

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


def all_prospects() -> list[dict]:
    return _load()


def existing_norms() -> set[str]:
    return {_norm(r.get("company", "")) for r in _load()}


def _clean_score(v: Any) -> int:
    try:
        return max(1, min(5, int(round(float(v)))))
    except Exception:
        return 3


def add_batch(rows: Iterable[dict], source: str = "researcher") -> dict:
    """Append a batch of prospect dicts, skipping duplicates by company name.

    Returns {added, skipped, total}. Safe to call repeatedly — dedupe is by
    normalised company name against the whole existing DB.
    """
    existing = _load()
    seen = {_norm(r.get("company", "")) for r in existing}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    added = 0
    skipped = 0
    n = len(existing)
    for r in rows:
        company = (r.get("company") or "").strip()
        key = _norm(company)
        if not company or key in seen:
            skipped += 1
            continue
        seen.add(key)
        n += 1
        existing.append({
            "id": f"P{n:04d}",
            "company": company,
            "industry": (r.get("industry") or "").strip(),
            "sub_sector": (r.get("sub_sector") or "").strip(),
            "location": (r.get("location") or "Myanmar").strip(),
            "size": (r.get("size") or "").strip(),
            "why_fit": (r.get("why_fit") or "").strip(),
            "fit_score": _clean_score(r.get("fit_score", 3)),
            "service_fit": (r.get("service_fit") or "").strip(),
            "website": (r.get("website") or "").strip(),
            "facebook": (r.get("facebook") or "").strip(),
            "phone": (r.get("phone") or "").strip(),
            "email": (r.get("email") or "").strip(),
            "source": (r.get("source") or source).strip(),
            "status": "new",
            "verified": False,
            "created_at": now,
        })
        added += 1
    if added:
        _save(existing)
    return {"added": added, "skipped": skipped, "total": len(existing)}


def seed_if_empty() -> int:
    """Load the shipped seed set on first ever run. Returns rows added."""
    if _load():
        return 0
    try:
        seed = json.loads(_SEED.read_text(encoding="utf-8"))
        rows = seed.get("prospects", seed) if isinstance(seed, dict) else seed
        return add_batch(rows, source="seed").get("added", 0)
    except Exception:
        return 0


def mark_synced(ids: set[str], field: str = "hs_synced") -> None:
    """Flag prospects as pushed to an external system (e.g. HubSpot) so a
    re-run never duplicates them."""
    rows = _load()
    changed = False
    for r in rows:
        if r.get("id") in ids and not r.get(field):
            r[field] = True
            changed = True
    if changed:
        _save(rows)


def set_status(company_or_id: str, status: str) -> dict | None:
    if status not in STATUSES:
        return None
    rows = _load()
    q = (company_or_id or "").lower().strip()
    for r in rows:
        if r.get("id", "").lower() == q or q and q in r.get("company", "").lower():
            r["status"] = status
            _save(rows)
            return r
    return None


# ── querying ──────────────────────────────────────────────────────────────────

def search(query: str = "", industry: str = "", min_fit: int = 0) -> list[dict]:
    q = (query or "").lower().strip()
    ind = (industry or "").lower().strip()
    out = []
    for r in _load():
        if ind and ind not in (r.get("industry", "") + " " + r.get("sub_sector", "")).lower():
            continue
        if min_fit and r.get("fit_score", 0) < min_fit:
            continue
        if q:
            hay = " ".join(str(r.get(k, "")) for k in
                           ("company", "industry", "sub_sector", "why_fit", "location", "service_fit")).lower()
            if q not in hay:
                continue
        out.append(r)
    return out


def recent(days: int = 1) -> list[dict]:
    cutoff = datetime.now() - timedelta(days=days)
    out = []
    for r in _load():
        try:
            if datetime.strptime(r.get("created_at", ""), "%Y-%m-%d %H:%M") >= cutoff:
                out.append(r)
        except Exception:
            continue
    return out


def stats() -> dict:
    rows = _load()
    by_ind: dict[str, int] = {}
    by_status: dict[str, int] = {}
    hot = 0
    for r in rows:
        by_ind[r.get("industry", "?")] = by_ind.get(r.get("industry", "?"), 0) + 1
        by_status[r.get("status", "new")] = by_status.get(r.get("status", "new"), 0) + 1
        if r.get("fit_score", 0) >= 4:
            hot += 1
    return {
        "total": len(rows),
        "hot": hot,
        "added_today": len(recent(1)),
        "added_week": len(recent(7)),
        "by_industry": dict(sorted(by_ind.items(), key=lambda x: -x[1])),
        "by_status": by_status,
    }


def format_prospect(r: dict) -> str:
    stars = "★" * r.get("fit_score", 0) + "☆" * (5 - r.get("fit_score", 0))
    lines = [
        f"<b>{r.get('company', '?')}</b> <i>[{r.get('id', '')}]</i>  {stars}",
        f"   {r.get('industry', '')}"
        + (f" · {r.get('sub_sector')}" if r.get("sub_sector") else "")
        + (f" · {r.get('location')}" if r.get("location") else ""),
    ]
    if r.get("why_fit"):
        lines.append(f"   💡 {r['why_fit']}")
    if r.get("service_fit"):
        lines.append(f"   🎯 Fit: {r['service_fit']}")
    contact = " ".join(x for x in [r.get("website"), r.get("facebook"), r.get("phone"), r.get("email")] if x)
    lines.append(f"   🔗 {contact}" if contact else "   🔗 contact: to research")
    return "\n".join(lines)


def stats_text() -> str:
    s = stats()
    if not s["total"]:
        return "No prospects yet. Run /research to collect the first batch."
    top = " · ".join(f"{k} {v}" for k, v in list(s["by_industry"].items())[:5])
    return (
        f"📊 <b>Prospect DB:</b> {s['total']} businesses · {s['hot']} hot (★★★★+)\n"
        f"🆕 +{s['added_today']} today · +{s['added_week']} this week\n"
        f"🏭 Top sectors: {top}"
    )
