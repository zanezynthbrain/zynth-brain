"""Abstract base class shared by every ZYNTH agent.

Concrete agents only need to supply a role description, a JSON Schema for
their structured output, and a prompt builder -- :class:`BaseAgent` takes
care of brand-consistent system prompts, calling the LLM with retries and
JSON-schema enforcement, writing results into the shared state, and
recording an audit-trail log entry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from config import ZYNTH_BRAND
from utils.knowledge import load_knowledge
from utils.llm_client import LLMClient, LLMCallError, MalformedOutputError
from utils.logging_config import get_logger
from utils.state import SharedMemory


class AgentError(Exception):
    """Raised when an agent cannot produce usable output after all retries."""


# Shared operating contract. Individual specs add role-specific method; these rules
# apply even when a compact legacy agent has not yet received its own deep spec.
_OPERATING_NON_NEGOTIABLES = """
ZYNTH OPERATING NON-NEGOTIABLES:
- Classify the requested work as internal exploration, proposal, execution, or external release. You may prepare internal work, but never claim approval or trigger/advise an external commitment without a named human decision.
- Separate confirmed facts, supplied claims, assumptions, hypotheses and open questions. Never invent client facts, metrics, budgets, vendors, legal permissions, partners, dates, performance results or cultural claims. Label unverified items clearly.
- Solve the business problem before selecting a deliverable. Tie recommendations to a specific audience, tension, objective, proposition, owner, timeline and measurement signal.
- For material creative, campaign, event, video, brand or sponsorship work, generate three genuinely distinct territories before recommending one; explain the selection rationale and production implications.
- Make outputs executable: state deliverables, dependencies, feasibility, commercial/rate assumptions, risks, QA checks, next owner and handoff. Treat all numbers as indicative until source-verified.
- A client-ready item must be strategically rooted, distinctive, feasible, commercially viable, measurable and safe. Flag any quality, brand, cultural, rights, data, legal or budget issue instead of hiding it.
- Do not publish, spend, contact clients/vendors, make bookings, or imply a real-world action occurred. Preserve founder and project-owner approval gates.
""".strip()


@dataclass
class AgentResult:
    """Outcome of a single agent run, ready to be merged into shared state."""

    agent: str
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0


class BaseAgent(ABC):
    """Common contract + plumbing for all ZYNTH marketing agents."""

    #: Namespace this agent reads/writes in :class:`SharedMemory`.
    agent_key: str = "base"
    #: Human-readable name surfaced in logs and orchestrator reports.
    display_name: str = "Base Agent"
    #: One-paragraph description of the agent's responsibility, folded
    #: into its system prompt alongside the ZYNTH brand voice.
    role_description: str = "A generic ZYNTH marketing agent."
    #: JSON Schema the agent's structured output must satisfy.
    output_schema: dict[str, Any] = {"type": "object", "properties": {}}
    #: Output-token budget for this agent's call. ``None`` uses the global
    #: per-call default. Agents producing long structured output (a 30-post
    #: content calendar, a design spec pack) must raise this or their JSON
    #: gets truncated and fails validation.
    max_output_tokens: int | None = None
    #: Route this agent to the cheaper fallback model. Set on high-volume
    #: drafting agents so running them through a workflow costs the same as
    #: running them through their own cost-shaped pipeline.
    use_fallback_model: bool = False

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm = llm_client or LLMClient()
        self.logger = get_logger(f"agents.{self.agent_key}")

    def build_system_prompt(self) -> str:
        """Compose the agent's persona: brand voice + role + knowledge + market FX."""
        prompt = (
            f"{ZYNTH_BRAND.as_system_prompt_block()}\n\n"
            f"Your specific role: {self.role_description}\n\n{_OPERATING_NON_NEGOTIABLES}"
        )
        # Seven-block operating spec for this agent, if one exists.
        from utils.specs import load_spec
        prompt += load_spec(self.agent_key)
        knowledge = load_knowledge()
        if knowledge:
            prompt += knowledge
        from utils.fx import rates_block
        prompt += rates_block()
        return prompt

    @abstractmethod
    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        """Build the task-specific prompt, pulling any upstream context from ``memory``."""
        raise NotImplementedError

    async def run(self, memory: SharedMemory, **kwargs: Any) -> AgentResult:
        """Execute this agent: prompt -> LLM -> validate -> persist -> log."""
        await memory.log(self.agent_key, "started")
        try:
            user_prompt = await self.build_user_prompt(memory, **kwargs)
            model = None
            if self.use_fallback_model:
                from config import get_settings
                model = get_settings().fallback_model_name
            data, response = await self.llm.complete_json(
                system=self.build_system_prompt(),
                user_prompt=user_prompt,
                schema=self.output_schema,
                max_tokens=self.max_output_tokens,
                model=model,
            )
        except (LLMCallError, MalformedOutputError) as exc:
            await memory.log(self.agent_key, "failed", error=str(exc))
            return AgentResult(agent=self.agent_key, success=False, error=str(exc))

        await memory.record_tokens(response.input_tokens, response.output_tokens)
        await memory.set(self.agent_key, data)
        await memory.log(
            self.agent_key,
            "completed",
            mocked=response.mocked,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        )
        return AgentResult(
            agent=self.agent_key,
            success=True,
            data=data,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        )
