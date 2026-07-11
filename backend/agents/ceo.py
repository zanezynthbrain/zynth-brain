"""CEO Agent — "The Director General".

The top of the ZYNTH leadership hierarchy. Responsible for:
  1. Setting the daily agenda and theme
  2. Assigning tasks to each department head (CMO, COO, CFO, HR)
  3. Reading all department outputs and facilitating a "leadership meeting"
     (multi-agent synthesis where departments respond to each other)
  4. Making key decisions, resolving conflicts between departments
  5. Compiling the final daily report and sending it via Telegram

The CEO doesn't do tactical work — it thinks strategically and holds
the other agents accountable.

CEO ဆိုတာ — strategy သတ်မှတ်တယ်၊ task assign လုပ်တယ်၊
leadership meeting ကြပ်မတ်တယ်၊ နောက်ဆုံးမှာ report ဆွဲပြီး Telegram ပို့တယ်။
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from agents.base import BaseAgent
from config import ZYNTH_BRAND
from utils.state import SharedMemory
from utils.storage import save_report
from utils.telegram import (
    send_ceo_daily_brief,
    send_department_update,
    send_bd_brief,
    send_to_creative_group,
    send_to_marketing_group,
    send_to_gm_group,
)

# ---- Agenda-setting schema (Phase 1) ------------------------------------
_AGENDA_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["date", "daily_theme", "focus_areas", "department_directives", "portfolio_brand_today"],
    "properties": {
        "date": {"type": "string"},
        "daily_theme": {"type": "string"},
        "focus_areas": {"type": "array", "items": {"type": "string"}},
        "department_directives": {
            "type": "object",
            "required": ["cmo", "coo", "cfo", "hr"],
            "properties": {
                "cmo": {"type": "string"},
                "coo": {"type": "string"},
                "cfo": {"type": "string"},
                "hr": {"type": "string"},
            },
        },
        "portfolio_brand_today": {"type": "string"},
        "priority_level": {"type": "string"},
    },
}

# ---- Meeting synthesis schema (Phase 3) ---------------------------------
_CEO_FINAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["daily_theme", "meeting_notes", "key_decisions", "action_items", "executive_summary", "tomorrow_priorities"],
    "properties": {
        "daily_theme": {"type": "string"},
        "meeting_notes": {"type": "string"},
        "key_decisions": {"type": "array", "items": {"type": "string"}},
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["item", "assigned_to", "due"],
                "properties": {
                    "item": {"type": "string"},
                    "assigned_to": {"type": "string"},
                    "due": {"type": "string"},
                },
            },
        },
        "executive_summary": {"type": "string"},
        "tomorrow_priorities": {"type": "array", "items": {"type": "string"}},
        "department_grades": {
            "type": "object",
            "properties": {
                "cmo": {"type": "string"},
                "coo": {"type": "string"},
                "cfo": {"type": "string"},
                "hr": {"type": "string"},
            },
        },
    },
}


class CEOAgent(BaseAgent):
    """The Director General — sets agenda, runs the meeting, sends the daily report."""

    agent_key = "ceo"
    display_name = "CEO — Director General"
    role_description = (
        "You are the CEO of ZYNTH, a digital marketing agency. You set the strategic "
        "direction, assign meaningful work to your leadership team (CMO, COO, CFO, HR), "
        "run the daily leadership meeting, make decisions when departments conflict, and "
        "hold everyone accountable to ZYNTH's growth goals. You think long-term, act "
        "decisively, and communicate with executive clarity. You care about outcomes, "
        "not activity."
    )
    output_schema: dict[str, Any] = _CEO_FINAL_SCHEMA

    async def build_user_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        return await self._build_synthesis_prompt(memory, **kwargs)

    async def run_full_day(self, memory: SharedMemory) -> dict[str, Any]:
        """Execute the full CEO daily cycle: set agenda → run departments → meeting → report."""
        today = datetime.now().strftime("%A, %B %d, %Y")

        # Phase 1: CEO sets the daily agenda
        await memory.log(self.agent_key, "setting_agenda")
        agenda = await self._set_agenda(memory, today)
        await memory.set("ceo_agenda", agenda)
        await memory.log(self.agent_key, "agenda_set", theme=agenda.get("daily_theme"))

        # Phase 2: Run all department agents in parallel
        await memory.log(self.agent_key, "running_departments")
        await self._run_departments(memory)

        # Phase 3: CEO runs the leadership meeting (reads all dept outputs, synthesizes)
        await memory.log(self.agent_key, "running_leadership_meeting")
        result = await self.run(memory)

        final_output = result.data or {}
        final_output["date"] = today
        await memory.set("ceo_final", final_output)

        # Save the daily report and send to Telegram
        save_report(final_output, "ceo_daily_report", department="reports/ceo")
        await send_ceo_daily_brief(final_output, date=today)

        # Department summaries also go to Telegram
        await self._send_department_telegrams(memory)

        await memory.log(self.agent_key, "day_complete")
        return final_output

    async def _set_agenda(self, memory: SharedMemory, today: str) -> dict[str, Any]:
        system = self.build_system_prompt()
        prompt = (
            f"Today is {today}. Set the daily agenda for ZYNTH.\n\n"
            "Produce: (1) a daily theme (one inspiring/strategic phrase), (2) 3-5 strategic "
            "focus areas for today, (3) specific directives for CMO, COO, CFO, and HR "
            "(what each should prioritize TODAY), (4) which portfolio brand the creative "
            "team should work on today, (5) the urgency/priority level: normal/high/crisis."
        )
        data, response = await self.llm.complete_json(system=system, user_prompt=prompt, schema=_AGENDA_SCHEMA)
        await memory.record_tokens(response.input_tokens, response.output_tokens)
        return data

    async def _run_departments(self, memory: SharedMemory) -> None:
        """Run all departments in three sequential waves so context flows properly.

        Wave 0 — Research: market intelligence goes into shared memory first.
        Wave 1 — Leadership + Ops: CMO/COO/CFO/HR/Events/Operations run in
                  parallel; CMO can read research, ops are largely independent.
        Wave 2 — Creative + BD specialists: read from both research AND CMO
                  direction before producing their outputs.
        """
        from agents.cmo import CMOAgent
        from agents.coo import COOAgent
        from agents.cfo import CFOAgent
        from agents.hr import HRAgent
        from agents.event_manager import EventManagerAgent
        from agents.operations import OperationsAgent
        from agents.portfolio import PortfolioAgent
        from agents.research_seo import MarketResearchSEOAgent
        from agents.copywriter import ContentCopywriterAgent
        from agents.lead_gen import LeadGenOutreachAgent

        # Wave 0: Research first — everything downstream benefits from this
        await memory.log(self.agent_key, "wave_0_research")
        research_result = await MarketResearchSEOAgent(self.llm).run(memory)
        if not research_result.success:
            await memory.log(self.agent_key, "research_failed", error=research_result.error)

        # Wave 1: Leadership + Operations in parallel (CMO reads research)
        await memory.log(self.agent_key, "wave_1_leadership")
        wave1 = [
            CMOAgent(self.llm),
            COOAgent(self.llm),
            CFOAgent(self.llm),
            HRAgent(self.llm),
            EventManagerAgent(self.llm),
            OperationsAgent(self.llm),
        ]
        results = await asyncio.gather(*[a.run(memory) for a in wave1])
        for r in results:
            if not r.success:
                await memory.log(self.agent_key, "department_failed", dept=r.agent, error=r.error)

        # Wave 2: Creative + BD specialists — read research + CMO direction
        await memory.log(self.agent_key, "wave_2_specialists")
        agenda = await memory.get("ceo_agenda", {})
        brand_name = agenda.get("portfolio_brand_today", "")
        if brand_name:
            from agents.portfolio import PORTFOLIO_BRANDS
            brand_info = next((b for b in PORTFOLIO_BRANDS if b["brand"] == brand_name), None)
            if brand_info:
                await memory.set("portfolio_brand_today", brand_info)

        wave2 = [
            ContentCopywriterAgent(self.llm),
            LeadGenOutreachAgent(self.llm),
            PortfolioAgent(self.llm),
        ]
        await asyncio.gather(*[a.run(memory) for a in wave2])

    async def _build_synthesis_prompt(self, memory: SharedMemory, **kwargs: Any) -> str:
        agenda = await memory.get("ceo_agenda", {})
        research = await memory.get("research_seo", {})
        cmo = await memory.get("cmo", {})
        coo = await memory.get("coo", {})
        cfo = await memory.get("cfo", {})
        hr = await memory.get("hr", {})
        events = await memory.get("event_manager", {})
        ops = await memory.get("operations", {})
        portfolio = await memory.get("portfolio", {})
        lead_gen = await memory.get("lead_gen", {})
        copywriter = await memory.get("copywriter", {})
        qa_feedback = kwargs.get("qa_feedback", "")

        # Summarize research for the CEO (keep it tight)
        research_summary = ""
        if research:
            kws = research.get("high_intent_keywords", [])
            top_kw = [k.get("keyword", k) if isinstance(k, dict) else k for k in kws[:5]]
            focus = research.get("recommended_focus_areas", [])[:3]
            research_summary = f"Top keywords: {', '.join(top_kw)}. Focus: {', '.join(focus)}."

        # Summarize BD prospects
        bd_summary = ""
        if lead_gen:
            prospects = lead_gen.get("prospects", [])
            companies = [p.get("company", "?") for p in prospects[:3]]
            bd_summary = f"NOVA identified {len(prospects)} prospects today: {', '.join(companies)}."

        prompt = (
            f"Today's Agenda: {agenda}\n\n"
            "--- FULL AGENCY DAY REPORT ---\n"
            "All departments have run and submitted their outputs. "
            "Research ran first, its findings flowed into all specialist work. "
            "As CEO, review everything, identify alignment and conflicts, "
            "make decisions, and produce the daily leadership summary.\n\n"
            f"Market Research:\n{research_summary or research}\n\n"
            f"CMO Report:\n{cmo}\n\n"
            f"COO Report:\n{coo}\n\n"
            f"CFO Report:\n{cfo}\n\n"
            f"HR Report:\n{hr}\n\n"
            f"Event Manager:\n{events}\n\n"
            f"Operations:\n{ops}\n\n"
            f"Portfolio Creative (brand of the day):\n{portfolio}\n\n"
            f"Content & Copy:\n{copywriter}\n\n"
            f"BD / Lead Gen (NOVA):\n{bd_summary or lead_gen}\n\n"
            "Produce: (1) meeting notes — key highlights from each department, "
            "(2) key decisions you made, (3) action items for each department for tomorrow, "
            "(4) executive summary (3-4 sentences you'd send to the board), "
            "(5) tomorrow's priorities, (6) performance grade for each department head."
        )
        if qa_feedback:
            prompt += f"\n\nQA feedback to address: {qa_feedback}"
        return prompt

    async def _send_department_telegrams(self, memory: SharedMemory) -> None:
        # --- Route structured outputs to the right Telegram groups ---
        portfolio_data = await memory.get("portfolio", {})
        if portfolio_data:
            await send_to_creative_group(portfolio_data)

        lead_gen_data = await memory.get("lead_gen", {})
        if lead_gen_data:
            await send_bd_brief(lead_gen_data)

        research_data = await memory.get("research_seo", {})
        if research_data:
            await send_to_marketing_group(research_data)

        ceo_data = await memory.get("ceo_final", {})
        if ceo_data:
            await send_to_gm_group(ceo_data)

        # --- Fallback: leadership summaries to founder personal chat ---
        dept_map = [
            ("coo", "⚙️ Operations (COO)", "operations_priorities"),
            ("cfo", "💰 Finance (CFO)", "financial_priorities"),
            ("hr", "👥 HR", "hr_priorities"),
            ("event_manager", "🎪 Events", "active_event_pipeline"),
        ]
        for key, label, field in dept_map:
            data = await memory.get(key, {})
            if data:
                value = data.get(field, "")
                if isinstance(value, list):
                    summary = "\n".join(f"• {v}" for v in value[:3])
                else:
                    summary = str(value)[:300]
                await send_department_update(label, summary)
