"""Orchestrator Agent -- "The Director".

Routes client requests to the right specialist agents, runs them in
dependency order (parallelizing independent steps), enforces a
workflow-wide token budget, and acts as the quality-assurance gate before
any output is considered final: every agent result is scored by an
LLM-as-judge review against ZYNTH's brand/quality bar, with bounded
retries (feeding the QA feedback back into the agent) before the
orchestrator accepts or gives up on a step.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable

from agents.base import AgentResult, BaseAgent
from config import Settings, ZYNTH_BRAND, get_settings
from utils.llm_client import LLMClient
from utils.logging_config import get_logger
from utils.state import SharedMemory

logger = get_logger("agents.orchestrator")

# JSON Schema for the LLM-as-judge QA review the orchestrator runs on every
# agent's output before accepting it.
_QA_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["passed", "score", "feedback"],
    "properties": {
        "passed": {"type": "boolean"},
        "score": {"type": "number"},
        "feedback": {"type": "string"},
    },
}

# Routing classifier schema used by route_request().
_ROUTE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["workflow", "reasoning"],
    "properties": {
        "workflow": {
            "type": "string",
            "enum": [
                "full_campaign", "research_only", "content_only", "leads_only",
                "ads_only", "content_studio", "brand_content_month",
            ],
        },
        "reasoning": {"type": "string"},
    },
}


@dataclass
class WorkflowStep:
    """One node in the orchestrator's execution graph."""

    agent_key: str
    depends_on: list[str] = field(default_factory=list)


@dataclass
class FinalReport:
    """Consolidated result of a full orchestrator run."""

    workflow: str
    status: str
    agent_results: dict[str, AgentResult]
    total_tokens: int
    state_snapshot: dict[str, Any]


# Default end-to-end workflow: Research feeds Copywriter and Lead Gen in
# parallel; Paid Ads waits on Copywriter so it can reuse approved creative.
DEFAULT_WORKFLOW: list[WorkflowStep] = [
    WorkflowStep(agent_key="research_seo"),
    WorkflowStep(agent_key="copywriter", depends_on=["research_seo"]),
    WorkflowStep(agent_key="lead_gen", depends_on=["research_seo"]),
    WorkflowStep(agent_key="paid_ads", depends_on=["copywriter"]),
]

WORKFLOWS: dict[str, list[WorkflowStep]] = {
    # ----- Core marketing workflows (original 4 agents) -----
    "full_campaign": DEFAULT_WORKFLOW,
    "research_only": [
        WorkflowStep(agent_key="research_seo"),
    ],
    "content_only": [
        WorkflowStep(agent_key="research_seo"),
        WorkflowStep(agent_key="copywriter", depends_on=["research_seo"]),
    ],
    "leads_only": [
        WorkflowStep(agent_key="research_seo"),
        WorkflowStep(agent_key="lead_gen", depends_on=["research_seo"]),
    ],
    "ads_only": [
        WorkflowStep(agent_key="research_seo"),
        WorkflowStep(agent_key="copywriter", depends_on=["research_seo"]),
        WorkflowStep(agent_key="paid_ads", depends_on=["copywriter"]),
    ],
    # ----- Department workflows (full agency agents) -----
    # BD pipeline: research → NOVA picks prospects informed by real intel
    "bd_pipeline": [
        WorkflowStep(agent_key="research_seo"),
        WorkflowStep(agent_key="lead_gen", depends_on=["research_seo"]),
    ],
    # Creative pipeline: research → copy direction → portfolio executes
    "creative_pipeline": [
        WorkflowStep(agent_key="research_seo"),
        WorkflowStep(agent_key="copywriter", depends_on=["research_seo"]),
        WorkflowStep(agent_key="portfolio", depends_on=["copywriter"]),
    ],
    # Full agency campaign: all 4 original specialists chained
    "full_agency_campaign": [
        WorkflowStep(agent_key="research_seo"),
        WorkflowStep(agent_key="copywriter", depends_on=["research_seo"]),
        WorkflowStep(agent_key="lead_gen", depends_on=["research_seo"]),
        WorkflowStep(agent_key="paid_ads", depends_on=["copywriter", "lead_gen"]),
    ],
    # ----- Content & Design Studio -----
    # Strategy first, then the month's copy and the visual system in parallel,
    # then per-asset design specs. Every step passes the QA gate.
    "content_studio": [
        WorkflowStep(agent_key="brand_strategist"),
        WorkflowStep(agent_key="content_creator", depends_on=["brand_strategist"]),
        WorkflowStep(agent_key="design_director", depends_on=["brand_strategist"]),
        WorkflowStep(agent_key="designer", depends_on=["content_creator", "design_director"]),
    ],
    # The studio collaborating with the rest of the agency: research and the
    # campaign planner (CMO) set the direction, the studio produces the month,
    # paid ads picks up the boost-flagged posts.
    "brand_content_month": [
        WorkflowStep(agent_key="research_seo"),
        WorkflowStep(agent_key="cmo", depends_on=["research_seo"]),
        WorkflowStep(agent_key="brand_strategist", depends_on=["research_seo", "cmo"]),
        WorkflowStep(agent_key="content_creator", depends_on=["brand_strategist"]),
        WorkflowStep(agent_key="design_director", depends_on=["brand_strategist"]),
        WorkflowStep(agent_key="designer", depends_on=["content_creator", "design_director"]),
        WorkflowStep(agent_key="paid_ads", depends_on=["content_creator"]),
    ],
}


def _topological_groups(steps: list[WorkflowStep]) -> list[list[WorkflowStep]]:
    """Split workflow steps into ordered groups that can run in parallel."""
    remaining = {step.agent_key: step for step in steps}
    done: set[str] = set()
    groups: list[list[WorkflowStep]] = []

    while remaining:
        ready = [s for s in remaining.values() if all(dep in done for dep in s.depends_on)]
        if not ready:
            raise ValueError(f"Cyclic or unsatisfiable dependency among: {list(remaining)}")
        groups.append(ready)
        for step in ready:
            done.add(step.agent_key)
            del remaining[step.agent_key]
    return groups


class OrchestratorAgent:
    """Directs the multi-agent workflow and gates output quality."""

    def __init__(
        self,
        agents: dict[str, BaseAgent],
        llm_client: LLMClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.agents = agents
        self.llm = llm_client or LLMClient()
        self.settings = settings or get_settings()

    async def route_request(self, request_text: str) -> str:
        """Classify a free-text client request into one of the known workflows."""
        system = (
            f"{ZYNTH_BRAND.as_system_prompt_block()}\n\n"
            "You are ZYNTH's intake Director. Classify the client's request into "
            "exactly one workflow: full_campaign (default for broad/ambiguous asks), "
            "research_only, content_only (a few pieces of copy), leads_only, ads_only, "
            "content_studio (a month of social content AND design for one brand — "
            "8/10/16/30 posts, calendar, visual system), or brand_content_month (the "
            "same month, but preceded by market research and a campaign plan)."
        )
        data, _ = await self.llm.complete_json(
            system=system,
            user_prompt=f"Client request:\n{request_text}",
            schema=_ROUTE_SCHEMA,
        )
        workflow = data["workflow"]
        logger.info("Routed request to workflow=%s (%s)", workflow, data.get("reasoning"))
        return workflow

    async def run_workflow(
        self,
        client_brief: dict[str, Any],
        workflow: str = "full_campaign",
        agent_kwargs: dict[str, dict[str, Any]] | None = None,
    ) -> FinalReport:
        """Execute ``workflow`` end-to-end against a fresh shared memory instance."""
        if workflow not in WORKFLOWS:
            raise ValueError(f"Unknown workflow '{workflow}'. Known: {list(WORKFLOWS)}")

        steps = WORKFLOWS[workflow]
        missing = [s.agent_key for s in steps if s.agent_key not in self.agents]
        if missing:
            raise ValueError(
                f"Workflow '{workflow}' needs agent(s) {missing} which this orchestrator "
                f"wasn't built with. Registered: {sorted(self.agents)}"
            )
        groups = _topological_groups(steps)
        memory = SharedMemory(client_brief)
        agent_kwargs = agent_kwargs or {}
        results: dict[str, AgentResult] = {}
        aborted = False

        for group in groups:
            if aborted:
                for step in group:
                    results[step.agent_key] = AgentResult(
                        agent=step.agent_key, success=False, error="skipped: workflow aborted upstream"
                    )
                continue

            used_tokens = await memory.total_tokens()
            if used_tokens >= self.settings.max_tokens_per_workflow:
                logger.warning("Workflow token budget exhausted (%d used); aborting remaining steps", used_tokens)
                aborted = True
                for step in group:
                    results[step.agent_key] = AgentResult(
                        agent=step.agent_key, success=False, error="skipped: token budget exhausted"
                    )
                continue

            group_results = await asyncio.gather(
                *[
                    self._run_with_qa_gate(step.agent_key, memory, **agent_kwargs.get(step.agent_key, {}))
                    for step in group
                ]
            )
            for result in group_results:
                results[result.agent] = result
                if not result.success:
                    # A failed required step aborts anything still depending on it;
                    # simplest safe policy here is to abort the whole remaining workflow.
                    aborted = True

        total_tokens = await memory.total_tokens()
        snapshot = await memory.snapshot()
        status = "completed" if all(r.success for r in results.values()) else "completed_with_errors"
        return FinalReport(
            workflow=workflow,
            status=status,
            agent_results=results,
            total_tokens=total_tokens,
            state_snapshot=snapshot,
        )

    async def _run_with_qa_gate(self, agent_key: str, memory: SharedMemory, **kwargs: Any) -> AgentResult:
        """Run one agent, then gate its output through LLM-as-judge QA with bounded retries."""
        agent = self.agents[agent_key]
        qa_feedback: str | None = None

        for attempt in range(self.settings.max_agent_retries + 1):
            result = await agent.run(memory, qa_feedback=qa_feedback, **kwargs)
            if not result.success:
                logger.warning("%s failed on attempt %d: %s", agent_key, attempt + 1, result.error)
                if attempt == self.settings.max_agent_retries:
                    return result
                continue

            passed, score, feedback = await self._qa_review(agent, result)
            await memory.log(agent_key, "qa_review", passed=passed, score=score, attempt=attempt + 1)
            if passed or attempt == self.settings.max_agent_retries:
                return result

            logger.info("%s QA gate sent it back (score=%.2f): %s", agent_key, score, feedback)
            qa_feedback = feedback

        return result  # pragma: no cover - loop always returns above

    async def _qa_review(self, agent: BaseAgent, result: AgentResult) -> tuple[bool, float, str]:
        """Score an agent's output against ZYNTH's quality bar via LLM-as-judge."""
        system = (
            f"{ZYNTH_BRAND.as_system_prompt_block()}\n\n"
            "You are ZYNTH's Quality Assurance Director. Review the agent output below "
            "for brand-voice consistency, completeness, and actionability. Be strict but fair."
        )
        prompt = (
            f"Agent: {agent.display_name}\nRole: {agent.role_description}\n\n"
            f"Output to review:\n{result.data}\n\n"
            f"Score 0.0-1.0. Pass requires score >= {self.settings.qa_min_pass_score}."
        )
        data, _ = await self.llm.complete_json(system=system, user_prompt=prompt, schema=_QA_SCHEMA)
        score = float(data["score"])
        passed = bool(data["passed"]) and score >= self.settings.qa_min_pass_score
        return passed, score, data["feedback"]
