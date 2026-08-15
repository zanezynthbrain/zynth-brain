"""Async CLI entrypoint for the ZYNTH multi-agent marketing backend.

Run a sample end-to-end campaign workflow:

    python main.py
    python main.py --workflow research_only
    python main.py --brief '{"company": "Acme SaaS", "industry": "fintech"}'

Without an ``ANTHROPIC_API_KEY`` set, every agent runs in deterministic
mock mode so the full pipeline -- routing, dependency-ordered execution,
the QA gate, and report compilation -- can be exercised offline.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from agents import OrchestratorAgent, WORKFLOWS, build_content_studio, build_default_agents
from config import get_settings
from utils.logging_config import configure_logging, get_logger
from utils.tools import write_file

logger = get_logger("main")

DEFAULT_BRIEF = {
    "company": "Northstar Robotics",
    "industry": "B2B industrial automation SaaS",
    "goal": "Generate qualified pipeline for our new predictive-maintenance product line",
    "target_geos": ["Singapore", "Vietnam", "Philippines"],
    "monthly_budget_usd": 15000,
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a ZYNTH agent workflow")
    parser.add_argument(
        "--workflow",
        choices=list(WORKFLOWS.keys()),
        default="full_campaign",
        help="Which workflow graph to execute.",
    )
    parser.add_argument(
        "--brief",
        type=str,
        default=None,
        help="JSON-encoded client brief. Defaults to a sample Northstar Robotics brief.",
    )
    parser.add_argument(
        "--request",
        type=str,
        default=None,
        help="Free-text client request to route via the orchestrator instead of --workflow.",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Relative path (inside outputs/) to a performance CSV for the Paid Ads agent.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="report.json",
        help="Relative path (inside outputs/) to write the final report JSON.",
    )
    return parser.parse_args(argv)


async def run(argv: list[str] | None = None) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)

    args = parse_args(argv)
    client_brief = json.loads(args.brief) if args.brief else DEFAULT_BRIEF

    # Default specialists + the Content & Design Studio, so content_studio /
    # brand_content_month workflows are runnable from the CLI too.
    agents = {**build_default_agents(), **build_content_studio()}
    orchestrator = OrchestratorAgent(agents=agents)

    workflow = args.workflow
    if args.request:
        workflow = await orchestrator.route_request(args.request)
        logger.info("Orchestrator routed free-text request to workflow=%s", workflow)

    agent_kwargs: dict[str, dict] = {}
    if args.csv:
        agent_kwargs["paid_ads"] = {"csv_relative_path": args.csv}

    logger.info(
        "Running workflow='%s' (mock_mode=%s) for client=%s",
        workflow,
        orchestrator.llm.is_mocked,
        client_brief.get("company", "unknown"),
    )

    report = await orchestrator.run_workflow(client_brief, workflow=workflow, agent_kwargs=agent_kwargs)

    summary = {
        "workflow": report.workflow,
        "status": report.status,
        "total_tokens": report.total_tokens,
        "agents": {
            key: {"success": r.success, "error": r.error} for key, r in report.agent_results.items()
        },
    }
    print(json.dumps(summary, indent=2))

    write_file(
        args.out,
        json.dumps(
            {
                "workflow": report.workflow,
                "status": report.status,
                "total_tokens": report.total_tokens,
                "state": report.state_snapshot,
            },
            indent=2,
            default=str,
        ),
    )
    logger.info("Full report written to outputs/%s", args.out)

    return 0 if report.status == "completed" else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
