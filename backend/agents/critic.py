"""Critic agent — the hard QC gate on every client-grade artifact.

Scores an artifact 1–10 on five dimensions and returns a pass/fail verdict with
named reasons. Below 8 (or any financial-law breach) → the producing agent is
re-run with the reasons appended, up to 2 auto-cycles, then it escalates to the
MD. The score + reasons ride in the Telegram caption. Runs on the PRIMARY model
(quality judgement is not a place to cheap out).
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory

PASS_MARK = 8.0

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["overall_score", "verdict", "dimensions", "reasons"],
    "properties": {
        "overall_score": {"type": "number", "minimum": 1, "maximum": 10},
        "verdict": {"type": "string", "enum": ["pass", "revise"]},
        "dimensions": {
            "type": "object",
            "properties": {
                "commercial_logic": {"type": "number", "minimum": 1, "maximum": 10},
                "market_grounding": {"type": "number", "minimum": 1, "maximum": 10},
                "concept_distinctiveness": {"type": "number", "minimum": 1, "maximum": 10},
                "completeness": {"type": "number", "minimum": 1, "maximum": 10},
                "financial_law_compliance": {"type": "number", "minimum": 1, "maximum": 10},
            },
        },
        "reasons": {"type": "array", "items": {"type": "string"}},
        "must_fix": {"type": "array", "items": {"type": "string"}},
    },
}


class CriticAgent(BaseAgent):
    """Scores client-grade artifacts against the ZYNTH output contract."""

    agent_key = "critic"
    display_name = "Critic (QC Gate)"
    role_description = (
        "You are ZYNTH's ruthless quality critic. You score client-grade artifacts "
        "1-10 on five dimensions and give an honest pass/revise verdict with specific, "
        "named reasons — never vague praise. You reward commercial logic, real MM/SG "
        "market numbers, distinctive defensible concepts, completeness (no empty "
        "sections), and financial-law compliance. Anything below 8, or any breach of "
        "the 35% margin floor / market-FX / verified-number rules, is a REVISE with "
        "concrete must-fix items."
    )
    output_schema = _SCHEMA

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:  # pragma: no cover
        return self._prompt(kwargs.get("artifact", ""), kwargs.get("kind", "artifact"))

    @staticmethod
    def _prompt(artifact: str, kind: str) -> str:
        return (
            f"Score this {kind} against the ZYNTH output contract.\n\n"
            "Dimensions (1-10 each): commercial_logic, market_grounding (real MM/SG "
            "numbers at market FX, not vague), concept_distinctiveness (could only be "
            "this brand), completeness (no empty/placeholder sections), "
            "financial_law_compliance (35% margin floor, 50% deposit, verified-vs-"
            "indicative tagged, market FX not CBM).\n"
            "overall_score = your holistic 1-10. verdict = 'pass' only if overall >= 8 "
            "AND financial_law_compliance >= 8 AND completeness >= 7. Otherwise 'revise' "
            "with specific must_fix items an agent can act on.\n\n"
            f"=== ARTIFACT ===\n{artifact[:12000]}"
        )

    async def critique(self, artifact: str, kind: str = "artifact",
                       memory: SharedMemory | None = None) -> dict[str, Any]:
        """Score an artifact. Returns the critique dict (mock-safe offline)."""
        mem = memory or SharedMemory(client_brief={"agency": "ZYNTH", "mode": "critic"})
        data, response = await self.llm.complete_json(
            system=self.build_system_prompt(),
            user_prompt=self._prompt(artifact, kind),
            schema=_SCHEMA,
            max_tokens=2000,
        )
        await mem.record_tokens(response.input_tokens, response.output_tokens)
        # Normalise verdict against the hard rule regardless of what the model said.
        score = float(data.get("overall_score", 0) or 0)
        dims = data.get("dimensions", {}) or {}
        fin = float(dims.get("financial_law_compliance", 10) or 10)
        comp = float(dims.get("completeness", 10) or 10)
        data["verdict"] = "pass" if (score >= PASS_MARK and fin >= 8 and comp >= 7) else "revise"
        return data


def caption(critique: dict[str, Any]) -> str:
    """One-line Telegram caption for a critique."""
    v = critique.get("verdict", "revise")
    icon = "✅" if v == "pass" else "🔁"
    score = critique.get("overall_score", "?")
    reasons = critique.get("must_fix") or critique.get("reasons") or []
    tail = ("" if v == "pass" else " — " + "; ".join(reasons[:2])) if reasons else ""
    return f"{icon} Critic {score}/10{tail}"
