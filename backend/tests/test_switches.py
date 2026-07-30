"""Feature-switch system tests (offline)."""


def test_defaults_are_quiet_md_only(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils import switches
    # fresh install → MD-only, nothing autonomous runs
    assert switches.md_only() is True
    assert switches.enabled("morning_brief") is False
    assert switches.enabled("daily_proposals") is False


def test_master_gates_all_jobs(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils import switches
    # turning a job on does nothing while the master is off
    switches.set_switch("daily_proposals", True)
    assert switches.enabled("daily_proposals") is False
    # wake the master → the job now runs; others still follow their own switch
    switches.set_active()
    assert switches.enabled("daily_proposals") is True
    assert switches.enabled("morning_brief") is False
    # quiet again silences everything
    switches.set_quiet()
    assert switches.enabled("daily_proposals") is False


def test_unknown_switch_rejected(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils import switches
    assert switches.set_switch("not_a_switch", True) is False


def test_dashboard_exposes_switches(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils.dashboard import build_state
    st = build_state()
    assert "switches" in st and "md_only" in st
    assert st["md_only"] is True
    assert any(s["name"] == "daily_proposals" for s in st["switches"])
