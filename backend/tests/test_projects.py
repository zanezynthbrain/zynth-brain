"""Projects — the unit of work the dashboard is built around.

The point of this layer is that IGNITE is one row, not the system. So the tests
care about the pipeline behaving like a pipeline, the money maths being right,
and bad input being refused rather than silently stored.
"""

from __future__ import annotations

import pytest

from utils import projects as P


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "_FILE", tmp_path / "projects.json")
    yield


def test_add_returns_a_row_with_id_slug_and_history():
    row = P.add("Shwe Pay Launch", client="Shwe Pay", kind="campaign",
                value_mmk=45_000_000, event_date="2026-10-01")
    assert row["id"] and row["slug"] == "shwe-pay-launch"
    assert row["stage"] == "lead"
    assert row["history"][0]["note"] == "created"


@pytest.mark.parametrize("kwargs, msg", [
    ({"name": ""}, "name"),
    ({"name": "X", "stage": "banana"}, "stage"),
    ({"name": "X", "kind": "hologram"}, "kind"),
    ({"name": "X", "market": "UK"}, "market"),
    ({"name": "X", "value_mmk": -5}, "negative"),
])
def test_bad_input_is_refused(kwargs, msg):
    with pytest.raises(ValueError, match=msg):
        P.add(**kwargs)


def test_set_stage_moves_the_project_and_keeps_an_audit_trail():
    row = P.add("Launch")
    P.set_stage(row["id"], "proposal", note="sent to client")
    P.set_stage(row["id"], "won", note="signed")

    after = P.get(row["id"])
    assert after["stage"] == "won"
    stages = [h["stage"] for h in after["history"]]
    assert stages == ["lead", "proposal", "won"]
    assert "signed" in after["history"][-1]["note"]


def test_set_stage_rejects_an_unknown_stage():
    row = P.add("Launch")
    with pytest.raises(ValueError):
        P.set_stage(row["id"], "maybe")


def test_get_works_by_id_or_slug():
    row = P.add("IGNITE Summit")
    assert P.get(row["id"])["name"] == "IGNITE Summit"
    assert P.get("ignite-summit")["id"] == row["id"]


def test_update_ignores_protected_fields():
    row = P.add("Launch", value_mmk=1_000_000)
    P.update(row["id"], client="New Client", value_mmk=2_000_000,
             id="hacked", history=[], created_at="1999-01-01")

    after = P.get(row["id"])
    assert after["client"] == "New Client"
    assert after["value_mmk"] == 2_000_000
    assert after["id"] == row["id"]                 # not overwritable
    assert after["created_at"] == row["created_at"]
    assert after["history"]                          # not wiped


def test_remove_returns_false_for_an_unknown_id():
    assert P.remove("nope") is False
    row = P.add("Launch")
    assert P.remove(row["id"]) is True
    assert P.get(row["id"]) is None


def test_summary_weights_the_pipeline_by_stage():
    P.add("A", stage="lead", value_mmk=10_000_000)       # x0.1 = 1.0M
    P.add("B", stage="proposal", value_mmk=10_000_000)   # x0.3 = 3.0M
    P.add("C", stage="won", value_mmk=10_000_000)        # x0.9 = 9.0M

    s = P.summary()
    assert s["active"] == 3
    assert s["pipeline_mmk"] == 30_000_000
    assert s["expected_mmk"] == 13_000_000


def test_closed_projects_leave_the_pipeline_but_stay_in_won_total():
    P.add("Delivered", stage="done", value_mmk=20_000_000)
    P.add("Lost one", stage="lost", value_mmk=50_000_000)

    s = P.summary()
    assert s["active"] == 0
    assert s["pipeline_mmk"] == 0
    assert s["won_mmk"] == 20_000_000       # done counts, lost does not


def test_days_to_handles_past_future_and_junk():
    from datetime import date, timedelta
    assert P.days_to("") is None
    assert P.days_to("not-a-date") is None
    assert P.days_to((date.today() + timedelta(days=5)).isoformat()) == 5
    assert P.days_to((date.today() - timedelta(days=3)).isoformat()) == -3


def test_board_returns_every_stage_even_when_empty():
    P.add("A", stage="won")
    board = P.board()
    assert set(board) >= set(P.STAGES)
    assert len(board["won"]) == 1
    assert board["lost"] == []


def test_upcoming_is_sorted_by_urgency():
    from datetime import date, timedelta
    P.add("Far", event_date=(date.today() + timedelta(days=90)).isoformat())
    P.add("Near", event_date=(date.today() + timedelta(days=5)).isoformat())
    names = [u["name"] for u in P.summary()["upcoming"]]
    assert names[0] == "Near"


def test_seed_puts_ignite_on_the_board_as_one_row_only_once():
    assert P.seed_if_empty() == 1
    assert P.seed_if_empty() == 0               # never duplicates

    rows = P.all_projects()
    assert len(rows) == 1
    ignite = rows[0]
    assert "IGNITE" in ignite["name"]
    assert ignite["kind"] == "owned"
    assert ignite["value_mmk"] == 198_000_000


def test_corrupt_store_does_not_crash_the_dashboard():
    P._FILE.parent.mkdir(parents=True, exist_ok=True)
    P._FILE.write_text("{ not json")
    assert P.all_projects() == []
    assert P.summary()["total"] == 0
    assert P.add("Recovers")["stage"] == "lead"


def test_dashboard_state_exposes_projects_and_connectors():
    """The console is only useful if the state actually carries these."""
    from utils import dashboard
    state = dashboard.build_state()
    for key in ("projects", "project_summary", "project_board",
                "connections", "queue", "switches"):
        assert key in state, key


# ---- the dashboard write path (/api/project) ----

def test_api_add_stage_and_remove_round_trip():
    payload, status = P.handle_api({"action": "add", "name": "KBZ Fintech Launch",
                                    "client": "KBZ", "kind": "campaign",
                                    "value_mmk": 45_000_000, "event_date": "2026-12-01"})
    assert status == 200 and payload["ok"]
    pid = payload["project"]["id"]

    payload, status = P.handle_api({"action": "stage", "id": pid, "stage": "won",
                                    "note": "signed"})
    assert status == 200 and payload["project"]["stage"] == "won"
    assert payload["summary"]["won_mmk"] == 45_000_000

    payload, status = P.handle_api({"action": "remove", "id": pid})
    assert status == 200 and payload["project"]["removed"] is True
    assert P.get(pid) is None


def test_api_rejects_unknown_action_with_400():
    payload, status = P.handle_api({"action": "launch_rocket"})
    assert status == 400 and not payload["ok"]


def test_api_turns_bad_input_into_400_not_500():
    """A typo in the dashboard must not surface as a server error."""
    for body in ({"action": "add", "name": ""},
                 {"action": "add", "name": "X", "kind": "hologram"},
                 {"action": "add", "name": "X", "value_mmk": -1},
                 {"action": "add", "name": "X", "value_mmk": "not-a-number"}):
        payload, status = P.handle_api(body)
        assert status == 400, body
        assert payload["error"]


def test_api_returns_404_for_a_missing_project():
    for body in ({"action": "stage", "id": "ghost", "stage": "won"},
                 {"action": "update", "id": "ghost", "client": "X"},
                 {"action": "remove", "id": "ghost"}):
        payload, status = P.handle_api(body)
        assert status == 404, body


def test_api_remove_is_not_called_twice():
    """Regression: the remove branch once invoked remove() twice, so a second
    delete could report success against an already-deleted row."""
    row = P.add("Once")
    payload, status = P.handle_api({"action": "remove", "id": row["id"]})
    assert status == 200
    payload, status = P.handle_api({"action": "remove", "id": row["id"]})
    assert status == 404


# ---- founder confirmation boundary ----

def test_agent_discovered_lead_requires_founder_confirmation_before_proposal():
    row = P.add("Inbound Corporate Event Lead", source="agent", kind="event")
    assert row["founder_confirmation_required"] is True
    assert row["founder_approval"] == "pending"

    with pytest.raises(PermissionError, match="founder confirmation"):
        P.set_stage(row["id"], "proposal")

    approved = P.confirm(row["id"], "Managing Director", note="Proceed to proposal")
    assert approved and approved["founder_approval"] == "approved"
    P.set_stage(row["id"], "proposal")
    assert P.get(row["id"])["stage"] == "proposal"


def test_declined_lead_remains_blocked_and_preserves_audit_history():
    row = P.add("Unqualified Sponsorship Lead", source="agent", kind="sponsorship")
    declined = P.confirm(row["id"], "Managing Director", approve=False, note="Not a strategic fit")
    assert declined and declined["founder_approval"] == "declined"
    assert "founder declined" in declined["history"][-1]["note"]

    with pytest.raises(PermissionError):
        P.set_stage(row["id"], "proposal")


def test_api_can_approve_an_agent_lead_before_stage_movement():
    payload, status = P.handle_api({
        "action": "add", "name": "AI-discovered Lead", "source": "agent", "kind": "digital",
    })
    assert status == 200 and payload["project"]["founder_approval"] == "pending"
    pid = payload["project"]["id"]

    payload, status = P.handle_api({"action": "stage", "id": pid, "stage": "proposal"})
    assert status == 400 and "founder confirmation" in payload["error"]

    payload, status = P.handle_api({
        "action": "approve", "id": pid, "approved_by": "Managing Director", "note": "Create proposal",
    })
    assert status == 200 and payload["project"]["founder_approval"] == "approved"

    payload, status = P.handle_api({"action": "stage", "id": pid, "stage": "proposal"})
    assert status == 200 and payload["project"]["stage"] == "proposal"
