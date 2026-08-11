"""Proposal document builder — turn a stub into a client-ready document.

The pool holds ~75 proposal *concepts*: a title, an objective, an audience, a
budget band. That is a shortlist, not a proposal. What actually goes to a client
is the WAVE PAY / IGNITE standard — fourteen sections, a costed line-item
budget, a run of show, a vendor table with lead times, KPIs, a risk register
and terms.

This module is the bridge. It takes a concept (or a fresh brief) and produces
the full document, and — critically — it does the money itself rather than
trusting the model with it:

* every budget line is summed in Python, not by the LLM
* contingency, client price and margin are computed from the cost base
* R1 is enforced: a document that would price below the 35% floor is repriced
  to the 40% target and the adjustment is recorded, never silently applied

That last point matters. The WAVE PAY draft priced ZYNTH's fee at "18% of
project cost" and printed a 15.3% margin — below the floor, and 53M MMK
under-priced. A generator that can make that mistake at scale is worse than no
generator, so the arithmetic lives here where it can be tested.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: Market FX, sell side. Sourced from knowledge/24; refreshed by the fx job.
FX_MMK_PER_USD = 4400

#: R1 — the financial law. Below FLOOR is blocked; TARGET is what we price at.
MARGIN_FLOOR = 0.35
MARGIN_TARGET = 0.40
CONTINGENCY = 0.10
DEPOSIT = 0.50

#: The fourteen sections of the ZYNTH Proposal Standard, in order.
SECTIONS = [
    "executive_summary", "concept_and_creative_direction", "event_details",
    "run_of_show", "stage_and_production_design", "vendor_requirements",
    "marketing_and_promotion", "budget", "commercial_model", "timeline",
    "kpis", "risk_register", "terms", "why_zynth",
]


@dataclass
class BudgetLine:
    category: str
    item: str
    qty: float
    unit_cost_mmk: float

    @property
    def total_mmk(self) -> float:
        return round(self.qty * self.unit_cost_mmk, 2)


@dataclass
class Costing:
    """The money, computed — never taken on trust from a model."""
    lines: list[BudgetLine] = field(default_factory=list)

    @property
    def subtotal_mmk(self) -> float:
        return round(sum(l.total_mmk for l in self.lines), 2)

    @property
    def contingency_mmk(self) -> float:
        return round(self.subtotal_mmk * CONTINGENCY, 2)

    @property
    def cost_base_mmk(self) -> float:
        """Everything ZYNTH must actually pay out."""
        return round(self.subtotal_mmk + self.contingency_mmk, 2)

    def price_at(self, margin: float) -> float:
        """Client price that yields `margin` on the cost base.

        Margin is on REVENUE (price), not a mark-up on cost — pricing a "35%
        fee on cost" only yields a 26% margin, which is how proposals drift
        under the floor without anyone noticing.
        """
        if not 0 <= margin < 1:
            raise ValueError("margin must be between 0 and 1")
        return round(self.cost_base_mmk / (1 - margin), 2)

    def margin_at(self, price_mmk: float) -> float:
        if price_mmk <= 0:
            return 0.0
        return (price_mmk - self.cost_base_mmk) / price_mmk

    def by_category(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for l in self.lines:
            out[l.category] = round(out.get(l.category, 0) + l.total_mmk, 2)
        return out


#: Pricing at exactly the target lands a hair under it in float arithmetic
#: (cost/0.6 then (price-cost)/price = 0.39999…), which would band a correct
#: quote as amber. Compare with a tolerance well below any real decision.
_EPS = 1e-9


def band(margin: float) -> str:
    """R1 banding — green >=40%, amber 35-39.9%, red below the floor."""
    if margin >= MARGIN_TARGET - _EPS:
        return "green"
    if margin >= MARGIN_FLOOR - _EPS:
        return "amber"
    return "red"


def commercial_model(costing: Costing, proposed_price_mmk: float | None = None
                     ) -> dict[str, Any]:
    """Build the commercial section, enforcing R1.

    If no price is proposed, we price at the target. If one is proposed and it
    falls below the floor, it is REPRICED to the target and the change is
    reported — the caller can show it to the MD, but it can never ship a
    sub-floor number to a client by accident.
    """
    cost = costing.cost_base_mmk
    target_price = costing.price_at(MARGIN_TARGET)

    adjustments: list[str] = []
    if proposed_price_mmk is None:
        price = target_price
    else:
        price = float(proposed_price_mmk)
        m = costing.margin_at(price)
        if m < MARGIN_FLOOR:
            adjustments.append(
                f"Proposed price {price:,.0f} MMK gives a {m*100:.1f}% margin, "
                f"below the {MARGIN_FLOOR*100:.0f}% floor (R1). Repriced to the "
                f"{MARGIN_TARGET*100:.0f}% target: {target_price:,.0f} MMK "
                f"(+{target_price - price:,.0f})."
            )
            price = target_price

    margin = costing.margin_at(price)
    return {
        "cost_base_mmk": cost,
        "subtotal_mmk": costing.subtotal_mmk,
        "contingency_mmk": costing.contingency_mmk,
        "client_price_mmk": round(price, 2),
        "client_price_usd": round(price / FX_MMK_PER_USD, 2),
        "zynth_profit_mmk": round(price - cost, 2),
        "margin_pct": round(margin * 100, 1),
        "band": band(margin),
        "floor_price_mmk": costing.price_at(MARGIN_FLOOR),
        "target_price_mmk": target_price,
        "deposit_mmk": round(price * DEPOSIT, 2),
        "fx_rate": FX_MMK_PER_USD,
        "adjustments": adjustments,
        "payment_terms": (
            f"{int(DEPOSIT*100)}% deposit on signature (R2), 30% four weeks "
            "before delivery, 20% within 7 days of the final report."
        ),
    }


def costing_from_rows(rows: list[dict[str, Any]]) -> Costing:
    """Build a Costing from loosely-typed model output, skipping junk lines."""
    lines: list[BudgetLine] = []
    for r in rows or []:
        if not isinstance(r, dict):
            continue
        try:
            qty = float(r.get("qty") or 1)
            unit = float(r.get("unit_cost_mmk") or r.get("unit_cost") or 0)
        except (TypeError, ValueError):
            continue
        if unit <= 0:
            continue
        lines.append(BudgetLine(
            category=str(r.get("category") or "Other")[:60],
            item=str(r.get("item") or "")[:120],
            qty=qty, unit_cost_mmk=unit,
        ))
    return Costing(lines)


def review(doc: dict[str, Any]) -> list[str]:
    """What is wrong with this document? Empty list means it is shippable."""
    problems: list[str] = []
    for s in SECTIONS:
        if not doc.get(s):
            problems.append(f"missing section: {s}")
    cm = doc.get("commercial_model") or {}
    if not cm:
        problems.append("missing commercial model")
    else:
        if cm.get("band") == "red":
            problems.append(
                f"margin {cm.get('margin_pct')}% is below the {MARGIN_FLOOR*100:.0f}% floor (R1)")
        if not cm.get("cost_base_mmk"):
            problems.append("budget has no costed lines")
    budget = doc.get("budget") or {}
    if isinstance(budget, dict) and not budget.get("lines"):
        problems.append("budget has no line items — a band is not a budget")
    return problems


__all__ = [
    "FX_MMK_PER_USD", "MARGIN_FLOOR", "MARGIN_TARGET", "CONTINGENCY", "DEPOSIT",
    "SECTIONS", "BudgetLine", "Costing", "band", "commercial_model",
    "costing_from_rows", "review",
]
