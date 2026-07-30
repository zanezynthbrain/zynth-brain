"""Event Operations register tests (offline)."""


def test_event_lifecycle_and_gate(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils import events as EV

    eid = EV.add_event({"client": "KBZ Bank", "event_type": "product launch",
                        "event_date": "2026-11-14", "guests": "300", "budget": "120M MMK"})
    assert eid == "E001"
    ev = EV.find("KBZ")
    assert ev and ev["stage"] == "enquiry" and ev["deposit_paid"] is False

    # advancing to confirmed without a deposit warns (the golden gate)
    ev, warn = EV.update_stage("E001", "confirmed")
    assert ev["stage"] == "confirmed" and "deposit" in warn.lower()

    # record the deposit, then the gate is clear
    EV.set_field("E001", "deposit_paid", "paid")
    ev, warn = EV.update_stage("E001", "preproduction")
    assert ev["stage"] == "preproduction" and warn == ""

    # checklist + pipeline reflect the state
    assert EV.next_todo(ev), "preproduction should have a working checklist"
    counts = EV.stage_counts()
    assert counts["preproduction"] == 1 and counts["enquiry"] == 0
    assert "KBZ" in EV.pipeline_stats()


def test_event_unknown_stage_rejected(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils import events as EV
    EV.add_event({"client": "Acme"})
    ev, warn = EV.update_stage("Acme", "banana")
    assert ev is None and "stage" in warn.lower()


def test_dashboard_state_includes_events(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils import events as EV
    EV.add_event({"client": "Yoma", "event_type": "gala", "stage": "confirmed", "deposit_paid": True})
    from utils.dashboard import build_state
    st = build_state()
    ev_dept = next(d for d in st["departments"] if d["name"] == "Events")
    labels = [w["label"] for w in ev_dept["works"]]
    assert "events" in labels and "confirmed" in labels
