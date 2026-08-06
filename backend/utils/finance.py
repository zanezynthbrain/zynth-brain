"""Operating cost register — the "Money Out" side of the finance system.

`FINANCE_operating_system.md` says the whole business runs off two lists: Money
In and Money Out. The proposal pool already carries revenue-side artifacts; this
is the other list — every recurring subscription and fixed cost ZYNTH pays to
stay switched on, plus the one-off top-ups (AI credits) that behave like stock
rather than like a subscription.

It answers three questions the MD actually asks:
  - What does it cost me to keep the lights on this month?  (`monthly_burn`)
  - What is the true cost of a portfolio film?              (`credit_plan`)
  - How long can I run before something must be paid?       (`runway`)

Standing rule applied: an amount nobody has verified against a real receipt is
stored with ``verified: false`` and is reported with a TBC tag. The burn total
is always given twice — confirmed only, and confirmed + estimated — so an
unverified figure can never quietly become a fact.

Storage follows the pool pattern: seed in backend/data/expenses.json, runtime
additions in outputs/proposal_pool/expenses_extra.json.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data"
_SEED = _DATA / "expenses.json"
_EXTRA = Path("outputs/proposal_pool/expenses_extra.json")

#: Cadences we understand, and their multiplier to a monthly figure.
CADENCE: dict[str, float] = {
    "monthly": 1.0,
    "yearly": 1 / 12,
    "quarterly": 1 / 3,
    "one_off": 0.0,      # capitalised, not part of the recurring burn
    "usage": 1.0,        # variable — the stored amount is the monthly ceiling
}

CATEGORIES = ("ai_tools", "infrastructure", "domain", "connectivity", "software", "other")


def _load(path: Path) -> list[dict]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("expenses", data) if isinstance(data, dict) else data
    except Exception:
        pass
    return []


def all_expenses() -> list[dict]:
    return _load(_SEED) + _load(_EXTRA)


def add_expense(record: dict[str, Any]) -> dict[str, Any]:
    """Log a cost. Unverified amounts stay flagged until a receipt confirms them."""
    if not record.get("item"):
        raise ValueError("An expense needs an 'item' name.")
    record.setdefault("cadence", "monthly")
    if record["cadence"] not in CADENCE:
        raise ValueError(f"Unknown cadence '{record['cadence']}'. Use: {sorted(CADENCE)}")
    record.setdefault("currency", "USD")
    record.setdefault("verified", False)
    record.setdefault("category", "other")
    record["logged_at"] = datetime.now().isoformat(timespec="seconds")
    extras = _load(_EXTRA)
    extras.append(record)
    _EXTRA.parent.mkdir(parents=True, exist_ok=True)
    _EXTRA.write_text(json.dumps(extras, indent=2, ensure_ascii=False), encoding="utf-8")
    return record


def verify_expense(item: str, amount_usd: float) -> dict | None:
    """Confirm an amount against a real receipt — the human half of the rule."""
    extras = _load(_EXTRA)
    for i, record in enumerate(extras):
        if record.get("item", "").lower() == item.lower():
            record.update(amount_usd=amount_usd, verified=True,
                          verified_at=datetime.now().isoformat(timespec="seconds"))
            extras[i] = record
            _EXTRA.write_text(json.dumps(extras, indent=2, ensure_ascii=False), encoding="utf-8")
            return record
    return None


def monthly_burn() -> dict[str, Any]:
    """The cost of staying switched on, split by how sure we are of it."""
    confirmed = estimated = 0.0
    unverified: list[str] = []
    by_category: dict[str, float] = {}

    for record in all_expenses():
        multiplier = CADENCE.get(record.get("cadence", "monthly"), 1.0)
        amount = float(record.get("amount_usd") or 0.0) * multiplier
        if not amount:
            continue
        if record.get("verified"):
            confirmed += amount
        else:
            estimated += amount
            unverified.append(record.get("item", "?"))
        category = record.get("category", "other")
        by_category[category] = round(by_category.get(category, 0.0) + amount, 2)

    return {
        "confirmed_usd": round(confirmed, 2),
        "estimated_usd": round(estimated, 2),
        "total_usd": round(confirmed + estimated, 2),
        "by_category": by_category,
        "unverified_items": unverified,
        "note": (
            "Estimated figures are UNVERIFIED — confirm each against a real receipt "
            "with /expenses verify <item> <amount>."
        ),
    }


def runway(cash_usd: float) -> dict[str, Any]:
    """Months of runway at the current burn. Deliberately uses the FULL burn."""
    burn = monthly_burn()["total_usd"]
    if burn <= 0:
        return {"months": None, "note": "No burn recorded yet."}
    months = cash_usd / burn
    return {
        "cash_usd": round(cash_usd, 2),
        "monthly_burn_usd": burn,
        "months": round(months, 1),
        "note": "Runway uses the full burn including unverified estimates — the safe side.",
    }


# ---------------------------------------------------------------------------
# AI generation credits — stock, not subscription
# ---------------------------------------------------------------------------

#: OpenArt credit cost per unit, as published by the platform (verified via API
#: 2026-08). A video unit is 5 seconds; an image unit is one image.
OPENART_RATES: dict[str, int] = {
    "gpt-image-2": 40,
    "nano-banana-pro": 40,
    "nano-banana-2": 20,
    "seedream-4-5": 15,
    "kling-image": 10,
    "pixverse-v6": 50,
    "wan-2-7": 125,
    "kling-3-omni": 175,
    "seedance-2-mini": 200,
    "gemini-omni-flash": 250,
    "seedance-2-fast": 350,
    "seedance-2": 400,
}

#: How many attempts a shot really takes. Generated shots fail; budgeting for a
#: single attempt per shot is the most common way an AI film runs over.
RETAKE_FACTOR = 1.35


#: Average on-screen shot length in a commercial cut. A 15s film is not three
#: 5-second shots — it is 7-9 shots of 1.5-2.5s each.
AVG_SHOT_SECONDS = 2.0

#: Minimum billable clip length: you pay for 5 seconds and use two of them.
CLIP_SECONDS = 5


def credit_plan(
    seconds: int,
    tier: str = "balanced",
    avg_shot_seconds: float = AVG_SHOT_SECONDS,
) -> dict[str, Any]:
    """Credits needed for one finished film, with retakes counted honestly.

    Pipeline assumed (the cheap, controllable one): generate a still plate per
    shot, then animate the plate. Text-to-video costs more and steers worse.

    **Credits scale with SHOT COUNT, not runtime.** Every shot is a separate
    generation billed at the 5-second minimum even when only 2 seconds reach
    the cut — so a fast-cut 15s film costs more than a slow 15s film, which is
    the opposite of how people assume it works.

    tier: "lean"      — volume models throughout, social-grade
          "balanced"  — volume B-roll, two hero shots that carry the idea
          "premium"   — hero model on every shot, brand-film grade
    """
    import math
    shots = max(1, math.ceil(seconds / max(0.5, avg_shot_seconds)))
    plates = shots * OPENART_RATES["gpt-image-2"]

    if tier == "lean":
        video = shots * OPENART_RATES["pixverse-v6"]
    elif tier == "premium":
        video = shots * OPENART_RATES["seedance-2"]
    elif tier == "balanced":
        heroes = min(2, shots)
        video = heroes * OPENART_RATES["seedance-2"] + (shots - heroes) * OPENART_RATES["wan-2-7"]
    else:
        raise ValueError("tier must be lean, balanced or premium")

    subtotal = plates + video
    total = int(round(subtotal * RETAKE_FACTOR))
    return {
        "seconds": seconds,
        "shots": shots,
        "generated_seconds": shots * CLIP_SECONDS,
        "tier": tier,
        "plate_credits": plates,
        "video_credits": video,
        "subtotal": subtotal,
        "retake_factor": RETAKE_FACTOR,
        "total_credits": total,
        "per_second": round(total / seconds, 1),
    }


def portfolio_plan(films: list[tuple[int, str]]) -> dict[str, Any]:
    """Credits for a slate of films, e.g. [(15, "balanced"), (30, "premium")]."""
    rows = [credit_plan(seconds, tier) for seconds, tier in films]
    total = sum(row["total_credits"] for row in rows)
    return {"films": rows, "total_credits": total}


def format_burn() -> str:
    """The burn as a Telegram-ready block."""
    burn = monthly_burn()
    lines = [
        "💸 <b>Monthly operating cost</b>",
        f"Confirmed: US${burn['confirmed_usd']:.2f}",
        f"Estimated (unverified): US${burn['estimated_usd']:.2f}",
        f"<b>Total: US${burn['total_usd']:.2f}/month</b>",
        "",
    ]
    for category, amount in sorted(burn["by_category"].items(), key=lambda kv: -kv[1]):
        lines.append(f"· {category.replace('_', ' ')}: US${amount:.2f}")
    if burn["unverified_items"]:
        lines.append("")
        lines.append("⚠️ TBC — confirm against a receipt: " + ", ".join(burn["unverified_items"]))
    return "\n".join(lines)


def format_expenses() -> str:
    """Every logged cost, one line each."""
    records = all_expenses()
    if not records:
        return "No costs logged yet. Add one: /expenses add <item> <amount> <cadence>"
    lines = []
    for record in sorted(records, key=lambda r: -(float(r.get("amount_usd") or 0))):
        tag = "" if record.get("verified") else "  ⚠️ TBC"
        amount = record.get("amount_usd")
        shown = f"US${float(amount):.2f}" if amount else "amount unknown"
        lines.append(
            f"· <b>{record.get('item', '?')}</b> — {shown} / {record.get('cadence', '?')}{tag}"
            + (f"\n   {record['note']}" if record.get("note") else "")
        )
    return "\n".join(lines)


__all__ = [
    "CADENCE", "CATEGORIES", "OPENART_RATES", "RETAKE_FACTOR",
    "AVG_SHOT_SECONDS", "CLIP_SECONDS",
    "all_expenses", "add_expense", "verify_expense", "monthly_burn", "runway",
    "credit_plan", "portfolio_plan", "format_burn", "format_expenses",
]
