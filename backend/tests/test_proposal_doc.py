"""Proposal document money — the arithmetic a client sees.

The WAVE PAY draft priced ZYNTH at "18% of project cost" and printed a 15.3%
margin: below the R1 floor and 54M MMK under-priced. Its own Production
subtotal was also 2.5M out. Both are the kind of mistake a generator would
repeat at scale, so the maths lives in Python and is tested here.
"""

from __future__ import annotations

import pytest

from utils import proposal_doc as PD


def rows(*specs):
    return [{"category": c, "item": i, "qty": q, "unit_cost_mmk": u}
            for c, i, q, u in specs]


def test_line_and_subtotal_arithmetic():
    c = PD.costing_from_rows(rows(("A", "x", 250, 50_000), ("B", "y", 8, 625_000)))
    assert c.subtotal_mmk == 17_500_000
    assert c.contingency_mmk == 1_750_000
    assert c.cost_base_mmk == 19_250_000


def test_margin_is_on_revenue_not_a_markup_on_cost():
    """A '40% fee on cost' is only a 28.6% margin — the classic under-pricing."""
    c = PD.costing_from_rows(rows(("A", "x", 1, 100_000_000 / 1.1)))
    price = c.price_at(0.40)
    assert c.margin_at(price) == pytest.approx(0.40)
    markup_price = c.cost_base_mmk * 1.40
    assert c.margin_at(markup_price) == pytest.approx(0.2857, abs=1e-3)


def test_pricing_at_target_bands_green_not_amber():
    """Float arithmetic once made an exactly-correct quote read as amber."""
    c = PD.costing_from_rows(rows(("A", "x", 1, 50_000_000)))
    cm = PD.commercial_model(c)
    assert cm["margin_pct"] == 40.0
    assert cm["band"] == "green"


@pytest.mark.parametrize("margin, expected", [
    (0.55, "green"), (0.40, "green"), (0.399, "amber"),
    (0.35, "amber"), (0.3499, "red"), (0.15, "red"), (0.0, "red"),
])
def test_banding_matches_r1(margin, expected):
    assert PD.band(margin) == expected


def test_a_sub_floor_price_is_repriced_and_reported():
    """The exact WAVE PAY defect: 129.1M on a 110M cost base."""
    c = PD.costing_from_rows(rows(("A", "x", 1, 100_000_000)))
    assert c.cost_base_mmk == 110_000_000

    cm = PD.commercial_model(c, proposed_price_mmk=129_149_000)
    assert cm["band"] == "green"
    assert cm["margin_pct"] == 40.0
    assert cm["client_price_mmk"] == pytest.approx(183_333_333, abs=1)
    assert cm["adjustments"], "a silent reprice is worse than no reprice"
    assert "below the 35% floor" in cm["adjustments"][0]


def test_a_healthy_price_is_left_alone():
    c = PD.costing_from_rows(rows(("A", "x", 1, 100_000_000)))
    cm = PD.commercial_model(c, proposed_price_mmk=220_000_000)
    assert cm["adjustments"] == []
    assert cm["margin_pct"] == 50.0


def test_deposit_and_usd_follow_the_final_price():
    c = PD.costing_from_rows(rows(("A", "x", 1, 100_000_000)))
    cm = PD.commercial_model(c, proposed_price_mmk=129_149_000)
    assert cm["deposit_mmk"] == pytest.approx(cm["client_price_mmk"] * 0.5, abs=1)
    assert cm["client_price_usd"] == pytest.approx(
        cm["client_price_mmk"] / PD.FX_MMK_PER_USD, abs=0.01)


def test_price_at_rejects_an_impossible_margin():
    c = PD.costing_from_rows(rows(("A", "x", 1, 1_000_000)))
    for bad in (1.0, 1.5, -0.1):
        with pytest.raises(ValueError):
            c.price_at(bad)


def test_junk_budget_rows_are_skipped_not_crashed_on():
    c = PD.costing_from_rows([
        {"category": "A", "item": "ok", "qty": 2, "unit_cost_mmk": 1_000_000},
        {"category": "B", "item": "free", "unit_cost_mmk": 0},
        {"category": "C", "item": "text", "unit_cost_mmk": "lots"},
        "not a dict", None,
    ])
    assert len(c.lines) == 1
    assert c.subtotal_mmk == 2_000_000


def test_by_category_totals():
    c = PD.costing_from_rows(rows(
        ("Production", "stage", 1, 20_000_000), ("Production", "lights", 1, 7_000_000),
        ("Catering", "food", 250, 50_000)))
    assert c.by_category() == {"Production": 27_000_000, "Catering": 12_500_000}


def test_review_flags_an_incomplete_or_sub_floor_document():
    problems = PD.review({})
    assert any("executive_summary" in p for p in problems)
    assert any("commercial model" in p for p in problems)

    doc = {s: "written" for s in PD.SECTIONS}
    doc["budget"] = {"lines": [1]}
    doc["commercial_model"] = {"band": "red", "margin_pct": 15.3,
                               "cost_base_mmk": 110_000_000}
    problems = PD.review(doc)
    assert len(problems) == 1
    assert "below the 35% floor" in problems[0]


def test_review_passes_a_complete_document():
    doc = {s: "written" for s in PD.SECTIONS}
    doc["budget"] = {"lines": [{"item": "x"}]}
    c = PD.costing_from_rows(rows(("A", "x", 1, 10_000_000)))
    doc["commercial_model"] = PD.commercial_model(c)
    assert PD.review(doc) == []


def test_a_band_is_not_a_budget():
    doc = {s: "written" for s in PD.SECTIONS}
    doc["budget"] = {"range": "20-30M MMK"}          # what the pool stubs carry
    c = PD.costing_from_rows(rows(("A", "x", 1, 10_000_000)))
    doc["commercial_model"] = PD.commercial_model(c)
    assert any("not a budget" in p for p in PD.review(doc))
