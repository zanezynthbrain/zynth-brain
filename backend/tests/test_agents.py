from agents import build_default_agents
from utils.state import SharedMemory


async def test_research_seo_agent_runs_in_mock_mode():
    agents = build_default_agents()
    memory = SharedMemory(client_brief={"company": "Acme", "industry": "fintech"})

    result = await agents["research_seo"].run(memory)

    assert result.success is True
    assert "competitor_landscape" in result.data
    assert await memory.get("research_seo") == result.data


async def test_copywriter_reads_upstream_research_context():
    agents = build_default_agents()
    memory = SharedMemory(client_brief={"company": "Acme"})
    await memory.set("research_seo", {"high_intent_keywords": [{"keyword": "x", "intent": "y", "est_monthly_volume": 1}]})

    result = await agents["copywriter"].run(memory)

    assert result.success is True
    assert "ad_copy" in result.data


async def test_paid_ads_agent_computes_roas_from_csv(tmp_path_factory=None):
    from utils.tools import write_file

    csv_text = "campaign,spend,revenue\nSummer Promo,1000,4000\nWinter Push,500,500\n"
    write_file("test_artifacts/perf.csv", csv_text)

    agents = build_default_agents()
    memory = SharedMemory(client_brief={"company": "Acme"})

    result = await agents["paid_ads"].run(memory, csv_relative_path="test_artifacts/perf.csv")

    assert result.success is True
    raw_metrics = await memory.get("paid_ads_raw_metrics")
    assert raw_metrics["overall_roas"] == 3.0
    assert raw_metrics["campaigns"][0]["campaign"] == "Summer Promo"
