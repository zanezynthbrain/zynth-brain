"""Brand profile store — the brand information the studio writes and designs for.

One record per client brand: who they are, who they're talking to, how they
sound, and what their design system already looks like. The Brand Strategist,
Content Creator, Design Director and Designer all read the SAME record, so a
brand's tone and palette can't drift between the caption and the artwork.

Storage follows the established pool pattern:
  seed      backend/data/brands.json                       (committed)
  runtime   outputs/proposal_pool/brands_extra.json        (pool-committed daily)

Nothing here is invented by an agent — profiles are added by the MD (via
/brandkit, free text structured by the cheap model). Fields left blank stay
blank; agents are told to ask rather than guess.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data"
_SEED = _DATA / "brands.json"
_EXTRA = Path("outputs/proposal_pool/brands_extra.json")

#: Canonical field order — also the shape /brandkit add asks the model for.
FIELDS: list[str] = [
    "brand",             # brand / client name
    "industry",
    "market",            # Myanmar / Singapore / both
    "positioning",       # what it stands for, in one line
    "products",          # what it actually sells
    "target_audience",   # primary audience, in the client's own words
    "audience_segments", # list of segments
    "audience_insight",  # the tension/motivation that makes them act
    "tone",              # tone of voice attributes
    "avoid",             # what the brand must never sound or look like
    "languages",         # e.g. "Myanmar + English"
    "palette",           # hex codes or colour names
    "fonts",
    "logo_notes",        # clear space, lockups, backgrounds
    "visual_style",      # photography/graphic direction already established
    "platforms",         # active channels + handles
    "competitors",
    "hashtags",
    "offers",            # current promos, price points, seasonal pushes
    "compliance",        # regulated claims, disclaimers, censorship notes
    "notes",
]

_LIST_FIELDS = {"audience_segments", "platforms", "competitors", "hashtags"}


def _load(path: Path) -> list[dict]:
    try:
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            return d.get("brands", d) if isinstance(d, dict) else d
    except Exception:
        pass
    return []


def all_brands() -> list[dict]:
    """Every brand profile: seed records first, runtime additions after."""
    return _load(_SEED) + _load(_EXTRA)


def names() -> list[str]:
    return [b.get("brand", "?") for b in all_brands()]


def find(query: str) -> dict | None:
    """Find one brand by name (exact, then case-insensitive substring)."""
    q = (query or "").strip().lower()
    if not q:
        return None
    brands = all_brands()
    for b in brands:
        if b.get("brand", "").strip().lower() == q:
            return b
    for b in brands:
        if q in b.get("brand", "").strip().lower():
            return b
    return None


def search(query: str = "") -> list[dict]:
    q = (query or "").lower().strip()
    if not q:
        return all_brands()
    out = []
    for b in all_brands():
        hay = " ".join(str(b.get(k, "")) for k in FIELDS).lower()
        if q in hay:
            out.append(b)
    return out


def add_brand(record: dict[str, Any]) -> dict[str, Any]:
    """Append (or update) a brand profile in the runtime store."""
    record = {k: v for k, v in record.items() if k in FIELDS and v not in (None, "", [])}
    if not record.get("brand"):
        raise ValueError("A brand profile needs at least a 'brand' name.")
    extras = _load(_EXTRA)
    name = record["brand"].strip().lower()
    for i, existing in enumerate(extras):
        if existing.get("brand", "").strip().lower() == name:
            existing.update(record)
            existing["updated_at"] = datetime.now().isoformat()
            extras[i] = existing
            _write(extras)
            return existing
    record["added_at"] = datetime.now().isoformat()
    extras.append(record)
    _write(extras)
    return record


def _write(extras: list[dict]) -> None:
    _EXTRA.parent.mkdir(parents=True, exist_ok=True)
    _EXTRA.write_text(json.dumps(extras, indent=2, ensure_ascii=False), encoding="utf-8")


def _fmt(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    return str(value)


def brand_block(query: str, max_chars: int = 2500) -> str:
    """Render one brand profile as a prompt block, or a STOP note if unknown.

    Agents receive either the real profile or an explicit instruction to work
    from the brief alone and flag what's missing — never a silent blank.
    """
    brand = find(query)
    if not brand:
        known = ", ".join(names()[:12]) or "none yet"
        return (
            "\n===== BRAND PROFILE =====\n"
            f"No stored profile for '{query}'. Work from the brief only, and list what "
            "you need (audience, tone, palette, fonts) under open_questions — do NOT "
            f"invent brand facts. Profiles on file: {known}. Add one with /brandkit add.\n"
            "===== END BRAND PROFILE =====\n"
        )
    lines = [f"{k.replace('_', ' ').title()}: {_fmt(brand[k])}" for k in FIELDS if brand.get(k)]
    body = "\n".join(lines)
    if len(body) > max_chars:
        body = body[:max_chars] + "\n…(profile truncated)"
    return (
        "\n===== BRAND PROFILE (authoritative — do not contradict) =====\n"
        f"{body}\n"
        "Anything not stated above is UNKNOWN: ask, don't invent.\n"
        "===== END BRAND PROFILE =====\n"
    )


def brands_summary() -> str:
    """One line per stored brand — for /brandkit list and status views."""
    brands = all_brands()
    if not brands:
        return "No brand profiles yet. Add one: /brandkit add <describe the brand>"
    out = []
    for b in brands:
        out.append(
            f"• {b.get('brand', '?')} — {b.get('industry', '?')} · {b.get('market', '?')} · "
            f"audience: {_fmt(b.get('target_audience', '—'))[:60]}"
        )
    return "\n".join(out)


__all__ = [
    "FIELDS", "all_brands", "names", "find", "search", "add_brand",
    "brand_block", "brands_summary",
]
