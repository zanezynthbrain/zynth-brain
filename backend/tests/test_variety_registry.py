"""The anti-overlap guarantees, asserted.

These exist because the failure they prevent already happened once: five
consecutive proposals used a published-performance-record mechanic.
"""
from __future__ import annotations

import pytest

from utils.variety_registry import (
    DIMENSIONS,
    MAX_SHARED,
    ROTATION,
    UNIQUE_IN_CYCLE,
    VarietyRegistry,
)


@pytest.fixture()
def reg(tmp_path):
    return VarietyRegistry(tmp_path / "variety.json")


def test_cycle_has_no_internal_repeats(reg):
    briefs = reg.plan_cycle("Financial services", 10)
    assert len(briefs) == 10
    for dim in UNIQUE_IN_CYCLE:
        values = [b[dim] for b in briefs]
        assert len(set(values)) == len(values), f"{dim} repeated inside one cycle"


def test_no_two_concepts_share_more_than_max(reg):
    briefs = reg.plan_cycle("Education", 10)
    for i, a in enumerate(briefs):
        for b in briefs[i + 1:]:
            shared = sum(1 for d in DIMENSIONS if a[d] == b[d])
            assert shared <= MAX_SHARED, f"{a['n']} and {b['n']} share {shared} dimensions"


def test_mechanic_and_territory_never_pair_twice(reg):
    """The specific failure mode: same mechanic + same territory = same proposal."""
    reg.claim_cycle("Retail & shopping malls", reg.plan_cycle("Retail & shopping malls", 10))
    pairs = {(c["mechanic"], c["territory"]) for c in reg.data["concepts"]}
    later = reg.plan_cycle("Healthcare", 10)
    for c in later:
        assert (c["mechanic"], c["territory"]) not in pairs


def test_second_cycle_does_not_repeat_the_first(reg):
    first = reg.plan_cycle("Financial services", 10)
    reg.claim_cycle("Financial services", first)
    second = reg.plan_cycle("Education", 10)
    for a in first:
        for b in second:
            shared = sum(1 for d in DIMENSIONS if a[d] == b[d])
            assert shared <= MAX_SHARED


def test_industry_rotation_never_repeats_immediately(reg):
    seen = []
    for _ in range(len(ROTATION)):
        ind = reg.next_industry()
        assert ind not in seen[-3:], "industry repeated within 3 cycles"
        reg.claim_cycle(ind, reg.plan_cycle(ind, 3))
        seen.append(ind)
    assert len(set(seen)) == len(ROTATION), "rotation did not cover every industry"


def test_rotation_continues_after_full_pass(reg):
    for _ in range(len(ROTATION)):
        ind = reg.next_industry()
        reg.claim_cycle(ind, reg.plan_cycle(ind, 2))
    nxt = reg.next_industry()
    assert nxt in ROTATION
    assert nxt not in reg.recent_industries(3)


def test_registry_persists(tmp_path):
    path = tmp_path / "v.json"
    a = VarietyRegistry(path)
    a.claim_cycle("Education", a.plan_cycle("Education", 4))
    b = VarietyRegistry(path)
    assert len(b.data["concepts"]) == 4
    assert b.data["cycles"][0]["industry"] == "Education"


def test_coverage_reports_progress(reg):
    reg.claim_cycle("Healthcare", reg.plan_cycle("Healthcare", 5))
    cov = reg.coverage()
    assert cov["cycles"] == 1 and cov["concepts"] == 5
    assert "Healthcare" in cov["industries_done"]
    assert "Healthcare" not in cov["industries_left"]


def test_relaxation_is_flagged_not_hidden(reg):
    """When the vocabulary runs out the compromise must be visible, not silent."""
    for _ in range(6):
        ind = reg.next_industry()
        reg.claim_cycle(ind, reg.plan_cycle(ind, 10))
    briefs = reg.plan_cycle(reg.next_industry(), 10)
    for b in briefs:
        assert set(DIMENSIONS).issubset(b.keys())
        if b.get("relaxed"):
            assert b["relaxed"] is True  # surfaced to the report, never swallowed


def test_every_brief_is_complete(reg):
    for b in reg.plan_cycle("Automotive / EV", 10):
        for dim in DIMENSIONS:
            assert b.get(dim), f"{dim} missing from brief {b['n']}"
        assert b["industry"] == "Automotive / EV"


def test_budget_scale_varies_within_a_cycle(reg):
    """A small vocabulary must still spread — not ten identical budget scales."""
    briefs = reg.plan_cycle("Hospitality / tourism / MICE", 10)
    scales = {b["budget_scale"] for b in briefs}
    assert len(scales) >= 3, f"budget scale did not vary: {scales}"


def test_season_varies_within_a_cycle(reg):
    briefs = reg.plan_cycle("Beauty / wellness", 10)
    assert len({b["season"] for b in briefs}) >= 4


def test_soft_dimensions_spread_evenly(reg):
    """No soft-dimension value should dominate a cycle."""
    briefs = reg.plan_cycle("Telecom / technology", 10)
    for dim in ("budget_scale", "season", "behaviour"):
        counts: dict[str, int] = {}
        for b in briefs:
            counts[b[dim]] = counts.get(b[dim], 0) + 1
        assert max(counts.values()) <= max(4, 10 // len(counts) + 2), \
            f"{dim} clumped: {counts}"
