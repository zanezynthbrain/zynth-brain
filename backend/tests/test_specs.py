"""Seven-block spec loader tests."""

from utils.specs import load_spec


def test_loads_existing_spec():
    block = load_spec("event_concept")
    assert "OPERATING SPEC" in block
    assert "Mandate" in block and "Handoff protocol" in block


def test_unknown_agent_returns_empty():
    assert load_spec("no_such_agent") == ""
    assert load_spec("") == ""


def test_master_proposal_spec_has_financial_law():
    block = load_spec("master_proposal")
    assert "35%" in block and "50% deposit" in block
