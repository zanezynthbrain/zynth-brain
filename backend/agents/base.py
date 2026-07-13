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

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm = llm_client or LLMClient()
        self.logger = get_logger(f"agents.{self.agent_key}")

    def build_system_prompt(self) -> str:
        """Compose the agent's persona: brand voice + role + knowledge + market FX."""
        prompt = f"{ZYNTH_BRAND.as_system_prompt_block()}\n\nYour specific role: {self.role_description}"
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
            data, response = await self.llm.complete_json(
                system=self.build_system_prompt(),
                user_prompt=user_prompt,
                schema=self.output_schema,
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
