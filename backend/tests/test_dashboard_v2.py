"""Command Center v2 + command-queue tests (offline)."""

from utils import cmdqueue


def test_build_state_has_v2_fields(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils.dashboard import build_state
    st = build_state()
    for k in ("cost", "pipeline", "deliverables", "directives", "sync_on", "scorecard", "departments"):
        assert k in st, f"missing {k}"
    assert "today" in st["cost"] and "cap" in st["cost"]
    assert isinstance(st["pipeline"], list) and len(st["pipeline"]) == 6  # 6 stages


def test_render_spa_is_the_hud(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils.dashboard import render_spa
    html = render_spa()
    assert "ZYNTH COMMAND" in html
    assert "Command Deck" in html and "System Vitals" in html
    assert "__STATE__" not in html  # state was injected


def test_cmdqueue_whitelist(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert cmdqueue.enqueue("brief") is True
    assert cmdqueue.enqueue("not_a_command") is False
    assert "brief" in cmdqueue.take_pending()
    assert cmdqueue.take_pending() == []  # drained
