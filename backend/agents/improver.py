"""Self-Improvement agent — ZYNTH looking at its own work and getting better.

The reflective loop. It reads what the agency actually did (activity), how it
performed (scorecard, cost, counts) and where it fell short (the mistake log),
finds the RECURRING failures and their root causes, and distils durable LESSONS
that get written back into every agent's prompt via utils/lessons.py.

Runs on the primary model (honest self-critique is not a place to cheap out).
Mock-safe offline like every other agent.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["health_score", "self_assessment", "recurring_mistakes", "lessons", "improvements"],
    "properties": {
        "health_score": {"type": "number", "minimum": 1, "maximum": 10},
        "self_assessment": {"type": "string"},
        "recurring_mistakes": {"type": "array", "items": {"type": "string"}},
        "root_causes": {"type": "array", "items": {"type": "string"}},
        "lessons": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["area", "lesson"],
                "properties": {
                    "area": {"type": "string"},
                    "lesson": {"type": "string"},
                },
            },
        },
        "improvements": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["action", "impact"],
                "properties": {
                    "action": {"type": "string"},
                    "impact": {"type": "string"},
                },
            },
        },
        "keep_doing": {"type": "array", "items": {"type": "string"}},
    },
}


class ImproverAgent(BaseAgent):
    """Reviews the agency's own work and produces lessons + concrete improvements."""

    agent_key = "improver"
    display_name = "Self-Improvement Loop"
    role_description = (
        "You are ZYNTH's self-improvement mind — brutally honest, specific, and "
        "constructive. You review the agency's OWN recent work and metrics, name the "
        "RECURRING mistakes (not one-offs), find their real root cause, and turn each "
        "into a durable, actionable LESSON that will change how the agents behave next "
        "time. You never give vague praise; every lesson must be concrete enough that an "
        "agent could follow it. You also flag what is genuinely working, so it is kept. "
        "Your lessons become binding knowledge injected into every agent — write them as "
        "clear imperatives (\"Always…\", \"Never…\", \"When X, do Y\")."
    )
    output_schema = _SCHEMA

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        return self._prompt(kwargs.get("context", ""))

    @staticmethod
    def _prompt(context: str) -> str:
        return (
            "Review ZYNTH's own recent work below and improve the system.\n\n"
            "Do this:\n"
            "1. health_score (1-10): honest state of the agency's execution quality.\n"
            "2. self_assessment: 2-3 sentences — what's the real story, and the single "
            "biggest thing holding ZYNTH back right now.\n"
            "3. recurring_mistakes: the patterns that repeat (not isolated errors).\n"
            "4. root_causes: why they happen.\n"
            "5. lessons: 2-6 durable lessons as imperatives (area + lesson). These will be "
            "injected into EVERY agent's prompt forever — make them count and non-obvious.\n"
            "6. improvements: concrete actions (action + expected impact).\n"
            "7. keep_doing: what's working and must be protected.\n\n"
            "Be specific to the evidence. If the mistake log is thin, infer weaknesses from "
            "the metrics and activity. Do not invent problems that aren't shown.\n\n"
            f"=== EVIDENCE ===\n{context[:12000]}"
        )

    @staticmethod
    def gather_context() -> str:
        """Assemble the evidence block from live system state (best-effort)."""
        parts: list[str] = []
        try:
            from utils.mistakes import digest, stats
            parts.append("MISTAKE LOG (recent):\n" + digest(40))
            st = stats()
            parts.append(f"Mistake counts by area: {st.get('by_area', {})}")
        except Exception:
            pass
        try:
            from utils.costaudit import audit_text
            parts.append("COST / JOBS:\n" + audit_text().replace("<b>", "").replace("</b>", "")
                         .replace("<code>", "").replace("</code>", "").replace("<i>", "").replace("</i>", ""))
        except Exception:
            pass
        try:
            from utils.dashboard import build_state
            s = build_state()
            t = s.get("totals", {})
            parts.append(
                "SNAPSHOT: "
                f"prospects={t.get('prospects')} hot={t.get('prospects_hot')} leads={t.get('leads')} "
                f"proposals={t.get('proposals')} open_tasks={t.get('tasks_open')} reds={t.get('reds')} "
                f"open_value=S${t.get('open_value')}"
            )
            acts = s.get("activity", [])[:20]
            if acts:
                parts.append("RECENT ACTIVITY:\n" + "\n".join(
                    f"- [{a.get('department','')}] {a.get('text','')}" for a in acts))
            sc = [x for x in s.get("scorecard", []) if x.get("status") == "bad"]
            if sc:
                parts.append("RED KPIs: " + ", ".join(x.get("label", "") for x in sc))
        except Exception:
            pass
        try:
            from utils.lessons import summary_line
            parts.append("LESSONS ALREADY KNOWN: " + summary_line())
        except Exception:
            pass
        return "\n\n".join(parts) or "(no evidence available)"

    async def review(self, memory: SharedMemory | None = None) -> dict[str, Any]:
        """Run the self-review over live system evidence. Mock-safe offline."""
        mem = memory or SharedMemory(client_brief={"agency": "ZYNTH", "mode": "improve"})
        context = self.gather_context()
        data, response = await self.llm.complete_json(
            system=self.build_system_prompt(),
            user_prompt=self._prompt(context),
            schema=_SCHEMA,
            max_tokens=2500,
        )
        try:
            await mem.record_tokens(response.input_tokens, response.output_tokens)
        except Exception:
            pass
        return data


def caption(review: dict[str, Any]) -> str:
    """Short Telegram summary of a self-review."""
    score = review.get("health_score", "?")
    lessons = review.get("lessons", []) or []
    imp = review.get("improvements", []) or []
    top = ""
    if imp:
        top = " · next: " + (imp[0].get("action", "")[:80] if isinstance(imp[0], dict) else "")
    return f"🧠 Self-review {score}/10 · {len(lessons)} lesson(s){top}"
