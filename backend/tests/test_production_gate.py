"""Production-gate tests — daily concepts cannot become real creative jobs by accident."""

from __future__ import annotations

import pytest

from utils import creative_queue as CQ
from utils import daily_workforce as DW
from utils import projects as P
from utils import production_gate as PG


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "_FILE", tmp_path / "projects.json")
    monkeypatch.setattr(DW, "_ROOT", tmp_path / "daily_workforce")
    monkeypatch.setattr(CQ, "_FILE", tmp_path / "creative_queue.json")


def _daily_package(*, lane: str = "image") -> dict:
    return {
        "date": "2026-08-15",
        "packages": [{
            "id": "2026-08-15-1",
            "title": "A Safe Concept",
            "market": "MM",
            "industry": "Manufacturing & Industrial",
            "work_lane": "integrated_campaign",
            "work_lane_label": "Integrated Campaign",
            "production_lane": lane,
            "status": "internal_draft",
            "approval_status": "founder_review_required",
            "single_minded_proposition": "Make safety visible.",
            "creative_concept": "A human-first safety ritual.",
            "creative_direction": "Confident industrial craft.",
        }],
    }


def test_pending_agent_lead_cannot_authorise_production():
    DW.save_daily_run(_daily_package())
    project = P.add("Incoming Industrial Lead", source="agent", kind="campaign")

    with pytest.raises(PermissionError, match="founder confirmation"):
        PG.authorise_package(
            day="2026-08-15", package_id="2026-08-15-1", project_id=project["id"],
            approved_by="Managing Director",
        )

    assert CQ.counts()["pending"] == 0


def test_founder_approved_project_can_queue_a_founder_triggered_3d_job():
    DW.save_daily_run(_daily_package(lane="scene3d"))
    project = P.add("Approved Stage Project", source="agent", kind="stage_design")
    P.confirm(project["id"], "Managing Director", note="Develop concept")

    result = PG.authorise_package(
        day="2026-08-15", package_id="2026-08-15-1", project_id=project["id"],
        approved_by="Managing Director", note="Create the 3D preview",
    )

    assert result["job"]["kind"] == "scene3d"
    assert result["job"]["approval"]["project_id"] == project["id"]
    assert result["job"]["spec"]["automation_mode"] == "founder_triggered"
    saved = DW.load_daily_run("2026-08-15")
    assert saved and saved["packages"][0]["status"] == "production_authorised"


def test_template_auto_requires_an_approved_image_template():
    DW.save_daily_run(_daily_package(lane="image"))
    project = P.add("Approved Digital Project", source="agent", kind="digital")
    P.confirm(project["id"], "Managing Director")

    with pytest.raises(ValueError, match="template_id"):
        PG.authorise_package(
            day="2026-08-15", package_id="2026-08-15-1", project_id=project["id"],
            approved_by="Managing Director", automation_mode="template_auto",
        )


def test_template_auto_never_opens_3d_production():
    DW.save_daily_run(_daily_package(lane="scene3d"))
    project = P.add("Approved Stage Project", source="agent", kind="stage_design")
    P.confirm(project["id"], "Managing Director")

    with pytest.raises(PermissionError, match="limited to approved image templates"):
        PG.authorise_package(
            day="2026-08-15", package_id="2026-08-15-1", project_id=project["id"],
            approved_by="Managing Director", automation_mode="template_auto", template_id="social-v1",
        )
