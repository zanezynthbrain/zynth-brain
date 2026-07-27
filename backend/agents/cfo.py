"""Chief Financial Officer (CFO) / Finance Agent.

Reports to CEO. Owns financial planning, pricing strategies, proposal
budgets, cost control, and makes sure ZYNTH stays profitable on every
project. Also produces financial documentation for the back office.
"""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from utils.state import SharedMemory


class CFOAgent(BaseAgent):
    agent_key = "cfo"
    display_name = "CFO — Finance & Strategy"
    role_description = (
        "You are ZYNTH's CFO and Finance Lead. You own the numbers: pricing, budgets, "
        "proposals, profitability, and financial strategy. For every project or campaign "
        "the marketing and operations teams plan, you stress-test the numbers and ensure "
        "ZYNTH maintains healthy margins. You also develop standard pricing templates, "
        "payment terms, and financial SOPs so the team can quote clients consistently."
    )
    output_schema: dict[str, Any] = {
        "type": "object",
        "required": ["financial_priorities", "pricing_recommendations", "budget_analysis", "financial_documents_needed", "profitability_flags"],
        "properties": {
            "financial_priorities": {"type": "array", "items": {"type": "string"}},
            "pricing_recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["service", "recommended_price_range", "rationale"],
                    "properties": {
                        "service": {"type": "string"},
                        "recommended_price_range": {"type": "string"},
                        "rationale": {"type": "string"},
                    },
                },
            },
            "budget_analysis": {
                "type": "object",
                "required": ["summary", "cost_items", "margin_estimate"],
                "properties": {
                    "summary": {"type": "string"},
                    "cost_items": {"type": "array", "items": {"type": "string"}},
                    "margin_estimate": {"type": "string"},
                },
            },
            "financial_documents_needed": {"type": "array", "items": {"type": "string"}},
            "profitability_flags": {"type": "array", "items": {"type": "string"}},
        },
    }

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        ceo_agenda = await memory.get("ceo_agenda", {})
        cmo_output = await memory.get("cmo", {})
        operations_output = await memory.get("operations", {})
        qa_feedback = kwargs.get("qa_feedback", "")

        prompt = (
            "CEO Agenda:\n"
            f"{ceo_agenda}\n\n"
            "CMO campaign plans (with estimated budgets):\n"
            f"{cmo_output.get('campaign_ideas', [])}\n\n"
            "Operations vendor/resource requirements:\n"
            f"{operations_output.get('vendor_research', [])}\n\n"
            "You ARE the CFO — you do the finance work, you do not assign it (see "
            "Operating Principles). Zane has zero finance experience beyond payroll, so "
            "never hand him a task like 'complete the Q3 analysis'; produce the finished "
            "numbers and explain them in one plain-English line.\n\n"
            "Produce: (1) financial priorities for today, (2) pricing recommendations for "
            "ZYNTH's core services at real market rates (MMK/SGD, market FX), each holding "
            "the 35% margin floor, (3) a real budget analysis of this week's planned "
            "activities with an actual margin estimate and the working shown in the "
            "summary — not 'someone should analyse this' but the analysis itself. Then "
            "(4) in financial_documents_needed, WRITE the single most useful finance "
            "artifact that's missing as ready-to-use content (a filled quotation template, "
            "the payment-terms clause, an invoice format) rather than just naming it. "
            "(5) profitability flags or cost overruns to escalate to the MD — only real "
            "money decisions. The canonical, full finance system lives in "
            "docs/departments/FINANCE_operating_system.md — build on it, don't contradict it."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback to address: {qa_feedback}"
        return prompt
