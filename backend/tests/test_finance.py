"""Operating cost register and AI credit planning (offline)."""

import pytest

from utils import finance as FIN


# --- The verified/unverified split -----------------------------------------

def test_seeded_costs_load_and_split_by_confidence():
    burn = FIN.monthly_burn()

    assert burn["total_usd"] == pytest.approx(burn["confirmed_usd"] + burn["estimated_usd"])
    # The MD-reported connectivity figure is the only confirmed one at seed time.
    assert burn["confirmed_usd"] == pytest.approx(5.0)
    assert burn["unverified_items"], "unverified costs must be named, not hidden in a total"
    assert "TBC" not in str(burn["confirmed_usd"])


def test_unknown_amounts_do_not_inflate_the_burn():
    """OpenArt and the domain have no confirmed price — they must count as zero,
    never as a guess."""
    items = {e["item"]: e for e in FIN.all_expenses()}
    assert items["OpenArt (Starter)"]["amount_usd"] is None
    assert items["Domain — zynth.asia"]["amount_usd"] is None
    # A None amount contributes nothing rather than raising or defaulting.
    assert FIN.monthly_burn()["total_usd"] > 0


def test_yearly_costs_are_amortised_monthly(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    before = FIN.monthly_burn()["total_usd"]

    FIN.add_expense({"item": "Domain test", "amount_usd": 24.0, "cadence": "yearly"})
    after = FIN.monthly_burn()["total_usd"]

    # US$24/year is US$2/month in the burn — not US$24
    assert after - before == pytest.approx(2.0, abs=0.01)


def test_one_off_costs_are_excluded_from_recurring_burn(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    before = FIN.monthly_burn()["total_usd"]
    FIN.add_expense({"item": "OpenArt top-up", "amount_usd": 50.0, "cadence": "one_off"})
    assert FIN.monthly_burn()["total_usd"] == pytest.approx(before), \
        "a one-off top-up is stock, not a monthly commitment"


def test_add_and_verify_round_trip(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    record = FIN.add_expense({"item": "Canva Pro", "amount_usd": 15.0, "cadence": "monthly"})
    assert record["verified"] is False

    confirmed = FIN.verify_expense("canva pro", 12.99)
    assert confirmed and confirmed["verified"] is True
    assert confirmed["amount_usd"] == 12.99
    assert FIN.verify_expense("nothing here", 1.0) is None


def test_add_expense_validates(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="item"):
        FIN.add_expense({"amount_usd": 5})
    with pytest.raises(ValueError, match="cadence"):
        FIN.add_expense({"item": "x", "amount_usd": 5, "cadence": "fortnightly"})


def test_runway_uses_the_full_burn_not_the_confirmed_one():
    result = FIN.runway(600.0)
    burn = FIN.monthly_burn()
    assert result["monthly_burn_usd"] == burn["total_usd"]
    assert result["months"] == pytest.approx(600.0 / burn["total_usd"], rel=0.01)


# --- Credit planning --------------------------------------------------------

def test_credits_scale_with_shot_count_not_runtime():
    """The trap: a fast-cut 15s film costs MORE than a slow one, because every
    shot is a separate 5-second billed generation."""
    fast = FIN.credit_plan(15, "balanced", avg_shot_seconds=1.5)
    slow = FIN.credit_plan(15, "balanced", avg_shot_seconds=3.0)
    assert fast["shots"] > slow["shots"]
    assert fast["total_credits"] > slow["total_credits"]


def test_generated_seconds_exceed_runtime():
    plan = FIN.credit_plan(15, "lean")
    assert plan["generated_seconds"] > plan["seconds"], \
        "you pay for 5s per clip and use ~2s of it"


def test_tiers_are_ordered_and_retakes_included():
    lean = FIN.credit_plan(15, "lean")
    balanced = FIN.credit_plan(15, "balanced")
    premium = FIN.credit_plan(15, "premium")
    assert lean["total_credits"] < balanced["total_credits"] < premium["total_credits"]
    # every tier carries the retake factor — no single-attempt fantasies
    for plan in (lean, balanced, premium):
        assert plan["total_credits"] > plan["subtotal"]
        assert plan["retake_factor"] == FIN.RETAKE_FACTOR


def test_unknown_tier_is_rejected():
    with pytest.raises(ValueError, match="tier"):
        FIN.credit_plan(15, "cinematic-ultra")


def test_portfolio_plan_sums_a_slate():
    slate = FIN.portfolio_plan([(15, "balanced"), (15, "balanced"), (30, "premium")])
    assert len(slate["films"]) == 3
    assert slate["total_credits"] == sum(f["total_credits"] for f in slate["films"])


def test_format_burn_tags_unverified_figures():
    text = FIN.format_burn()
    assert "TBC" in text and "Confirmed" in text
    assert "Total" in text
