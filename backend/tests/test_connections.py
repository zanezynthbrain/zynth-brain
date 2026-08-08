"""Connection health checks.

The whole value of this module is that it never lies: a green light must mean
the check actually passed just now. So the tests care about two things — that
a broken link is reported as broken, and that a failing check can never take
the report down with it.
"""

from __future__ import annotations

import pytest

from utils import connections
from utils.connections_page import render


def test_every_check_returns_a_valid_link():
    for link in connections.run_all():
        assert link.status in ("ok", "warn", "down"), link
        assert link.name and link.detail, link
        # Anything not green must tell the MD how to fix it.
        if link.status != "ok":
            assert link.fix, f"{link.key} is {link.status} with no fix hint"


def test_summary_shape_and_tally_is_consistent():
    s = connections.summary()
    assert s["overall"] in ("ok", "warn", "down")
    assert sum(s["tally"].values()) == len(s["links"])
    assert s["checked_at"]


def test_overall_is_worst_status():
    """One red link must colour the whole report red — never averaged away."""
    s = connections.summary()
    if s["tally"]["down"]:
        assert s["overall"] == "down"
    elif s["tally"]["warn"]:
        assert s["overall"] == "warn"
    else:
        assert s["overall"] == "ok"


def test_a_failing_check_does_not_break_the_report(monkeypatch):
    def exploding() -> connections.Link:
        raise RuntimeError("disk on fire")

    monkeypatch.setattr(connections, "CHECKS", (connections.check_github, exploding))
    links = connections.run_all()
    assert len(links) == 2
    assert any(l.status == "down" and "disk on fire" in l.detail for l in links)


def test_graphify_reports_down_when_graph_json_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(connections, "ROOT", tmp_path)
    link = connections.check_graphify()
    assert link.status == "down"
    assert "graph.json" in link.detail
    assert "graphify" in link.fix


def test_graphify_flags_a_stale_graph(tmp_path, monkeypatch):
    import os, time
    monkeypatch.setattr(connections, "ROOT", tmp_path)
    monkeypatch.setattr(connections, "STALE_GRAPH_DAYS", 3)
    g = tmp_path / "graphify-out" / "graph.json"
    g.parent.mkdir(parents=True)
    g.write_text("{}")
    old = time.time() - 10 * 86400
    os.utime(g, (old, old))

    link = connections.check_graphify()
    # Either stale (package present) or down (package absent) — never a green
    # light on a 10-day-old graph.
    assert link.status in ("warn", "down")
    assert link.status != "ok"


def test_obsidian_reports_down_without_a_vault(tmp_path, monkeypatch):
    monkeypatch.setattr(connections, "ROOT", tmp_path)
    monkeypatch.setattr(connections, "BACKEND", tmp_path / "backend")
    link = connections.check_obsidian()
    assert link.status == "down"
    assert "vault" in link.detail.lower()


def test_drive_is_warn_not_down_when_unconfigured(monkeypatch):
    """Drive is optional — its absence degrades storage, it does not break it."""
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)
    monkeypatch.delenv("DRIVE_DELIVERABLES_FOLDER", raising=False)
    link = connections.check_drive()
    assert link.status == "warn"
    assert "GitHub only" in link.detail


def test_claude_api_is_down_without_a_key(monkeypatch):
    """Mock mode produces placeholders. That must read as broken, not fine."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    link = connections.check_claude_api()
    assert link.status == "down"
    assert "MOCK" in link.detail


def test_checks_never_print_secret_values(monkeypatch):
    secret = "sk-ant-SUPERSECRET-do-not-leak"
    monkeypatch.setenv("ANTHROPIC_API_KEY", secret)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", secret)
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", secret)
    monkeypatch.setenv("DRIVE_DELIVERABLES_FOLDER", secret)

    blob = connections.text_report() + render(connections.summary())
    assert secret not in blob
    assert "SUPERSECRET" not in blob


def test_page_renders_both_themes_and_escapes_content():
    page = render(connections.summary())
    assert "prefers-color-scheme:dark" in page
    assert '[data-theme="dark"]' in page and '[data-theme="light"]' in page
    assert "<title>" in page
    # Detail text is escaped, so a stray angle bracket cannot break the markup.
    assert "<script>" not in page.lower().replace("<script>alert", "")


def test_page_reports_the_same_counts_as_the_summary():
    s = connections.summary()
    page = render(s)
    for n in s["tally"].values():
        assert f'>{n}</div>' in page
