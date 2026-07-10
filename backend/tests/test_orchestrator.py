from agents import OrchestratorAgent, build_default_agents


async def test_full_campaign_workflow_runs_all_agents_and_passes_qa():
    agents = build_default_agents()
    orchestrator = OrchestratorAgent(agents=agents)

    report = await orchestrator.run_workflow(
        client_brief={"company": "Acme", "industry": "fintech"},
        workflow="full_campaign",
    )

    assert report.status == "completed"
    assert set(report.agent_results.keys()) == {"research_seo", "copywriter", "lead_gen", "paid_ads"}
    assert all(r.success for r in report.agent_results.values())


async def test_research_only_workflow_skips_other_agents():
    agents = build_default_agents()
    orchestrator = OrchestratorAgent(agents=agents)

    report = await orchestrator.run_workflow(
        client_brief={"company": "Acme"},
        workflow="research_only",
    )

    assert set(report.agent_results.keys()) == {"research_seo"}


async def test_route_request_returns_known_workflow():
    agents = build_default_agents()
    orchestrator = OrchestratorAgent(agents=agents)

    workflow = await orchestrator.route_request("We just need a competitor and keyword analysis")

    from agents import WORKFLOWS

    assert workflow in WORKFLOWS


async def test_unknown_workflow_raises_value_error():
    agents = build_default_agents()
    orchestrator = OrchestratorAgent(agents=agents)

    try:
        await orchestrator.run_workflow(client_brief={}, workflow="not_a_real_workflow")
        assert False, "expected ValueError"
    except ValueError:
        pass
