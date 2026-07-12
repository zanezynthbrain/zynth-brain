"""Resilient async wrapper around the Anthropic Claude API.

Centralizes everything every agent needs from an LLM call:

* **Token budgeting** -- per-call ``max_tokens`` caps plus a workflow-wide
  budget enforced by the orchestrator via :class:`~utils.state.SharedMemory`.
* **Structured retries** -- exponential backoff on transient API errors.
* **JSON repair loop** -- if the model returns malformed/non-conforming
  JSON, the client feeds the validation error back to the model and asks
  it to correct itself, up to a configurable number of attempts.
* **Mock mode** -- when no API key is configured, calls are served by a
  deterministic, schema-aware mock so the rest of the framework remains
  fully runnable/testable offline.
"""

from __future__ import annotations

import asyncio
import json
import random
from dataclasses import dataclass
from typing import Any

from config import Settings, get_settings
from utils.logging_config import get_logger
from utils.tools import validate_json

logger = get_logger(__name__)


class LLMCallError(Exception):
    """Raised when the underlying LLM API call fails after all retries."""


class MalformedOutputError(Exception):
    """Raised when the model cannot produce schema-conforming JSON in time."""


@dataclass
class LLMResponse:
    """Normalized result of a single LLM call."""

    text: str
    input_tokens: int
    output_tokens: int
    mocked: bool = False


class LLMClient:
    """Async Claude client with retry, budget, and JSON-repair behavior."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = None
        if self.settings.has_llm_credentials:
            from anthropic import AsyncAnthropic  # local import: optional dependency in mock mode

            self._client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)

    @property
    def is_mocked(self) -> bool:
        return self._client is None

    async def complete(
        self,
        system: str,
        user_prompt: str,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> LLMResponse:
        """Run a single completion with retry/backoff on transient failures.

        ``model`` overrides the default for this one call — used to route
        high-volume draft work to the cheaper fallback model.
        """
        if self.is_mocked:
            return self._mock_complete(user_prompt)

        budget = max_tokens or self.settings.max_tokens_per_call
        last_exc: Exception | None = None
        for attempt in range(1, self.settings.max_llm_retries + 1):
            try:
                response = await self._client.messages.create(
                    model=model or self.settings.model_name,
                    max_tokens=budget,
                    system=system,
                    messages=[{"role": "user", "content": user_prompt}],
                    timeout=self.settings.request_timeout_seconds,
                )
                text = "".join(block.text for block in response.content if block.type == "text")
                result = LLMResponse(
                    text=text,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                )
                # Record spend — raises CostBudgetExceeded if daily cap hit
                try:
                    from utils.cost_tracker import get_cost_tracker, CostBudgetExceeded
                    tracker = await get_cost_tracker()
                    await tracker.record(model or self.settings.model_name, result.input_tokens, result.output_tokens)
                except Exception as cost_exc:  # noqa: BLE001
                    from utils.cost_tracker import CostBudgetExceeded
                    if isinstance(cost_exc, CostBudgetExceeded):
                        raise LLMCallError(str(cost_exc)) from cost_exc
                return result
            except Exception as exc:  # noqa: BLE001 - any SDK/network error is retryable
                last_exc = exc
                backoff = (2 ** (attempt - 1)) + random.random()
                logger.warning(
                    "LLM call failed (attempt %d/%d): %s. Retrying in %.1fs",
                    attempt,
                    self.settings.max_llm_retries,
                    exc,
                    backoff,
                )
                if attempt < self.settings.max_llm_retries:
                    await asyncio.sleep(backoff)

        raise LLMCallError(f"LLM call failed after {self.settings.max_llm_retries} attempts: {last_exc}")

    async def complete_json(
        self,
        system: str,
        user_prompt: str,
        schema: dict[str, Any],
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> tuple[dict[str, Any], LLMResponse]:
        """Run a completion and guarantee the result validates against ``schema``.

        On a validation failure, the model is shown the exact error and
        asked to correct its previous output, up to
        ``settings.max_json_repair_attempts`` times before raising
        :class:`MalformedOutputError`.
        """
        if self.is_mocked:
            mock_data = _synthesize_from_schema(schema)
            result = validate_json(mock_data, schema)
            if not result.ok:  # pragma: no cover - defensive; mock synthesis should always validate
                raise MalformedOutputError(f"Mock synthesis failed to satisfy schema: {result.error}")
            return result.data, LLMResponse(text=json.dumps(mock_data), input_tokens=0, output_tokens=0, mocked=True)

        repair_note = ""
        last_error = ""
        for attempt in range(self.settings.max_json_repair_attempts + 1):
            prompt = (
                f"{user_prompt}\n\nRespond with ONLY valid JSON matching this JSON Schema "
                f"(no markdown fences, no commentary):\n{json.dumps(schema)}"
            )
            if repair_note:
                prompt += f"\n\nYour previous response was invalid: {last_error}\nReturn corrected JSON only."

            response = await self.complete(system, prompt, max_tokens=max_tokens, model=model)
            cleaned = _strip_markdown_fence(response.text)
            result = validate_json(cleaned, schema)
            if result.ok:
                return result.data, response

            last_error = result.error or "unknown validation error"
            repair_note = last_error
            logger.warning("JSON validation failed (attempt %d): %s", attempt + 1, last_error)

        raise MalformedOutputError(
            f"Model failed to produce schema-conforming JSON after "
            f"{self.settings.max_json_repair_attempts + 1} attempts: {last_error}"
        )

    def _mock_complete(self, user_prompt: str) -> LLMResponse:
        """Deterministic offline stand-in used when no API key is configured."""
        text = (
            "[MOCK RESPONSE - no ANTHROPIC_API_KEY configured] "
            f"Echoing prompt summary: {user_prompt[:120]}..."
        )
        return LLMResponse(text=text, input_tokens=len(user_prompt) // 4, output_tokens=len(text) // 4, mocked=True)


def _synthesize_from_schema(schema: dict[str, Any]) -> Any:
    """Generate a minimal, schema-conforming placeholder value.

    Used exclusively in offline mock mode so agents and the orchestrator's
    QA gate can be exercised end-to-end without an API key.
    """
    schema_type = schema.get("type", "object")

    if "enum" in schema:
        return schema["enum"][0]

    if schema_type == "object":
        properties = schema.get("properties", {})
        required = schema.get("required", list(properties.keys()))
        return {key: _synthesize_from_schema(properties[key]) for key in required if key in properties}

    if schema_type == "array":
        item_schema = schema.get("items", {"type": "string"})
        min_items = schema.get("minItems", 1)
        return [_synthesize_from_schema(item_schema) for _ in range(max(min_items, 1))]

    if schema_type == "string":
        return "[MOCK] sample value"

    if schema_type in ("number", "integer"):
        # Default to a small positive value (rather than 0) so mock-mode
        # scores/counts clear typical ">= threshold" checks (e.g. the
        # orchestrator's QA pass-score gate) instead of always failing them.
        minimum = schema.get("minimum", 1)
        return int(minimum) if schema_type == "integer" else float(minimum)

    if schema_type == "boolean":
        # Default mock booleans to True so offline demo runs (no API key) pass
        # the orchestrator's QA gate on the first attempt instead of churning
        # through retries against an LLM that isn't actually there to judge.
        return True

    return None


def _strip_markdown_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines)
    return stripped
