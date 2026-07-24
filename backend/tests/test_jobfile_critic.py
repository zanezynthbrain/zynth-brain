"""Job file + Critic QC gate tests (mock-mode safe)."""

import pytest

from utils import jobfile
from agents.critic import CriticAgent, caption


def test_jobfile_roundtrip_and_gates(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    job = jobfile.create("Launch event for a bank", market="MM", budget="MMK 100M")
    jid = job["id"]

    ok, missing = jobfile.has_sections(jid, ["concept", "ops"])
    assert not ok and set(missing) == {"concept", "ops"}

    jobfile.append_section(jid, "concept", {"name": "The Next Tier"})
    ok, missing = jobfile.has_sections(jid, ["concept"])
    assert ok and missing == []

    jobfile.add_blocking_question(jid, "event_ops", "What is the guest count?")
    assert jobfile.get(jid)["status"] == "blocked"

    jobfile.record_qc(jid, 8.5, "pass", [])
    assert jobfile.get(jid)["status"] == "approved"


@pytest.mark.asyncio
async def test_critic_returns_verdict_offline():
    critic = CriticAgent()
    result = await critic.critique("A short proposal draft.", kind="proposal")
    assert result["verdict"] in ("pass", "revise")
    assert "overall_score" in result
    line = caption(result)
    assert "Critic" in line
