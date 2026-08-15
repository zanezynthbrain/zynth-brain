"""Daily Agency Workforce tests — proactive ideas with founder-controlled release."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest

from utils import daily_workforce as DW


class StubLLM:
    """No-network structured-output stand-in for workflow tests."""

    async def complete_json(self, **_: object):
        package = {
            "title": "A distinct concept",
            "opportunity": "A timely internal opportunity",
            "business_objective": "Create qualified interest",
            "audience": "A defined audience",
            "human_insight": "People value useful progress",
            "single_minded_proposition": "Progress feels possible",
            "creative_concept": "A clear participatory idea",
            "why_this_can_work": "It connects a human tension to a brand role",
            "activation_system": ["tease", "participate", "share"],
            "channel_roles": ["social creates participation", "event makes it tangible"],
            "deliverables": ["proposal", "key visual", "measurement plan"],
            "kpi_hypothesis": ["qualified engagement", "intent signal"],
            "creative_direction": "Bold, accessible and typography-led",
            "client_explanation": "A concise founder-reviewable proposal explanation.",
            "assumptions": ["Client brand facts will be supplied before production."],
            "open_questions": ["Which client or lead is this for?"],
            "cultural_or_brand_risks": ["Validate local relevance before external use."],
        }
        return {"packages": [dict(package), dict(package), dict(package)]}, SimpleNamespace(
            mocked=False, input_tokens=12, output_tokens=34
        )


def test_daily_slots_are_three_distinct_work_lanes():
    slots = DW.daily_slots(date(2026, 8, 15))
    assert len(slots) == 3
    assert len({s["lane"] for s in slots}) == 3
    assert {s["market"] for s in slots} <= {"MM", "SG"}
    assert all(s["industry"] and s["production_lane"] for s in slots)


@pytest.mark.asyncio
async def test_daily_workforce_creates_only_internal_founder_reviewable_packages(tmp_path, monkeypatch):
    monkeypatch.setattr(DW, "_ROOT", tmp_path / "daily_workforce")

    payload = await DW.run_daily_workforce(day=date(2026, 8, 15), llm_client=StubLLM())

    assert payload["status"] == "founder_review_required"
    assert len(payload["packages"]) == 3
    assert (tmp_path / "daily_workforce" / "2026-08-15.json").exists()
    for package in payload["packages"]:
        assert package["status"] == "internal_draft"
        assert package["approval_status"] == "founder_review_required"
        assert package["client_contact_allowed"] is False
        assert package["production_allowed"] is False
        assert package["publishing_allowed"] is False


def test_summary_explicitly_states_that_release_is_not_authorised():
    text = DW.summary_text({
        "date": "2026-08-15",
        "packages": [{
            "id": "2026-08-15-1", "work_lane_label": "Corporate Event",
            "industry": "Technology & Startup", "market": "MM", "title": "A founder review",
        }],
    })
    assert "No client contact, publication or production has been authorised" in text
    assert "founder approval" in text.lower()
