from __future__ import annotations


def test_founder_ui_renders_with_live_state():
    from utils.founder_ui import render

    html = render({
        "generated": "Fri 15 Aug 2026, 11:30",
        "project_summary": {},
        "projects": [],
        "queue": {},
        "deliverables": [],
        "directives": [],
        "pipeline": [],
        "switches": [],
        "connections": {"overall": "warn", "links": []},
    })

    assert "ZYNTH COMMAND" in html
    assert "Decisions waiting for you" in html
    assert "Daily Creative Studio" in html
    assert "Information integrity" in html
    assert "__STATE__" not in html
    assert "client commitment" in html


def test_dashboard_state_exposes_creative_jobs(monkeypatch, tmp_path):
    from utils import dashboard

    monkeypatch.setattr(dashboard, "_POOL", tmp_path)
    state = dashboard.build_state()

    assert "creative_jobs" in state
    assert isinstance(state["creative_jobs"], list)


def test_dashboard_uses_founder_command_centre():
    from utils import dashboard

    html = dashboard.render_spa()

    assert "FOUNDER OPERATING SYSTEM" in html
    assert "Project portfolio" in html
    assert "Proposal Constellation" not in html
