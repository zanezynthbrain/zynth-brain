"""ZYNTH Telegram Bot — your AI agency in your pocket.

Commands:
    /brief          → Run full CEO daily brief (all departments)
    /status         → System status
    /report         → Load today's saved CEO report
    /bd             → Run NOVA BD agent — 3 prospects, approve/skip with buttons
    /pipeline       → Show your BD approval pipeline
    /creative       → Run creative portfolio → posts to Creative group
    /research       → Market research → posts to Marketing group
    /event          → Generate event proposal
    /ops            → Vendor research + SOP
    /run <workflow> → full_campaign / research_only / ads_only / leads_only
    /approve        → Confirm CEO action items
    /proposals      → Browse proposal data pool stats
    /generate       → Generate proposals (industry, month, market optional)
    /help           → All commands
"""

from __future__ import annotations

import asyncio
import sys
import time
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from agents import build_full_agency, FinalReport, OrchestratorAgent, WORKFLOWS
from agents.ceo import CEOAgent
from config import get_settings
from utils.approvals import (
    approve_prospect,
    get_all,
    get_pending,
    mark_contacted,
    pipeline_summary,
    skip_prospect,
)
from utils.logging_config import configure_logging, get_logger
from utils.llm_client import LLMClient
from utils.state import SharedMemory
from utils.storage import load_latest_report
from utils.telegram import (
    send_bd_brief,
    send_bd_brief_interactive,
    send_message,
    send_to_creative_group,
    send_to_gm_group,
    send_to_marketing_group,
)

logger = get_logger("telegram_bot")

# In-memory store for the last BD run — used by approve/skip callbacks
_bd_session: dict = {"prospects": [], "run_at": None}


async def _run_workflow(
    workflow: str,
    client_brief: dict,
    llm: LLMClient | None = None,
) -> FinalReport:
    """Run any workflow through the orchestrator with the full agency agent set.

    Every command that calls this gets proper context flow:
    agents earlier in the DAG write to SharedMemory → downstream agents read it.
    """
    _llm = llm or LLMClient()
    agents = build_full_agency(_llm)
    orchestrator = OrchestratorAgent(agents=agents, llm_client=_llm)
    return await orchestrator.run_workflow(client_brief=client_brief, workflow=workflow)


async def _post_init(application: Application) -> None:
    """Start the APScheduler once the asyncio event loop is running."""
    from scheduler import build_scheduler
    from utils.fx import refresh_rates
    settings = get_settings()
    scheduler = build_scheduler(settings)
    scheduler.start()
    application.bot_data["scheduler"] = scheduler
    try:
        await refresh_rates()  # best-effort live FX at startup
    except Exception:
        pass
    logger.info(
        "ZYNTH Scheduler started — brief at %02d:%02d, EOD at %02d:00 Yangon time",
        settings.daily_brief_hour,
        settings.daily_brief_minute,
        settings.eod_report_hour,
    )


async def _post_stop(application: Application) -> None:
    """Shut the scheduler down cleanly when the bot exits."""
    scheduler = application.bot_data.get("scheduler")
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)


def _get_application() -> Application:
    settings = get_settings()
    if not settings.has_telegram:
        raise RuntimeError(
            "Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
        )
    return (
        Application.builder()
        .token(settings.telegram_bot_token)
        .post_init(_post_init)
        .post_stop(_post_stop)
        .build()
    )


def _security_check(update: Update) -> bool:
    """Only respond to the configured owner chat. Silently ignore everything else."""
    settings = get_settings()
    return str(update.effective_chat.id) == settings.telegram_chat_id


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    pending = len(get_pending())
    pipeline_note = f"\n⚡ {pending} prospect(s) waiting for outreach → /pipeline" if pending else ""
    ignite_line = CEOAgent._ignite_countdown()
    ignite_note = f"\n{ignite_line}" if ignite_line else ""
    text = (
        "🧠 <b>ZYNTH AI Agency — Command Center</b>"
        f"{ignite_note}\n\n"
        "<b>BD & Sales:</b>\n"
        "/bd — NOVA runs BD: 3 prospects, approve/skip with buttons\n"
        "/pipeline — Show approved prospects + mark contacted\n\n"
        "<b>Daily Operations:</b>\n"
        "/brief — Full CEO daily brief (all departments)\n"
        "/report — Load today's saved CEO report\n"
        "/status — System status\n"
        "/cost — Today's API spend vs S$5 budget\n\n"
        "<b>Department Agents:</b>\n"
        "/creative — Creative brief → Creative group\n"
        "/research — Market intel → Marketing group\n"
        "/event &lt;brief&gt; — Event Specialist Team → full proposal + approve/revise 🎪\n"
        "/ops — Vendor research + SOP\n\n"
        "<b>Campaign Workflows:</b>\n"
        "/run full_campaign\n"
        "/run research_only\n"
        "/run ads_only\n"
        "/run leads_only\n\n"
        "<b>Proposal Factory:</b>\n"
        "/generate — Quick idea drafts (cheap model, fills the pool)\n"
        "/proposal &lt;brief&gt; — FULL client-ready proposal as a Word doc 📄\n"
        "/proposals — Browse proposal pool stats\n\n"
        "<b>Knowledge Base:</b>\n"
        "/kb — Which business knowledge files the agents are using\n"
        "/fx — MMK market rates used in every proposal (/fx set usd 4290 4400)\n"
        "/venue — Yangon venue DB (search · add · outreach email drafts)\n\n"
        "<b>Approvals:</b>\n"
        "/approve — Confirm CEO action items\n"
        "/help — This message\n\n"
        "💬 <i>Or just type anything — your AI Chief of Staff will answer.</i>\n"
        "🎙 <i>Voice messages work too — Burmese and English.</i>"
        f"{pipeline_note}"
    )
    await update.message.reply_html(text)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    settings = get_settings()
    llm = LLMClient()
    text = (
        "⚡ <b>ZYNTH System Status</b>\n\n"
        f"🤖 LLM: {'✅ Live (Claude)' if not llm.is_mocked else '🔵 Mock mode (no API key)'}\n"
        f"📱 Telegram: ✅ Connected\n"
        f"🌐 Network tools: {'✅ Enabled' if settings.allow_network else '🔵 Mock mode'}\n"
        f"🕐 Timezone: {settings.scheduler_timezone}\n"
        f"⏰ Daily brief: {settings.daily_brief_hour:02d}:{settings.daily_brief_minute:02d}\n"
        f"🌙 EOD report: {settings.eod_report_hour:02d}:00\n\n"
        "All agents operational. Send /brief to run the full day."
    )
    await update.message.reply_html(text)


async def cmd_brief(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    await update.message.reply_html(
        "🚀 <b>Running the full agency...</b>\n\n"
        "Wave 0 — Market Research (SG + MM)\n"
        "Wave 1 — CMO · COO · CFO · HR · Events · Ops (parallel)\n"
        "Wave 2 — Creative · NOVA BD · Copywriter (read research + CMO)\n"
        "Wave 3 — CEO Leadership Meeting + Report\n\n"
        "Reports routing to each group when ready. Takes ~2 min."
    )
    try:
        llm = LLMClient()
        memory = SharedMemory(client_brief={"agency": "ZYNTH", "market": "Singapore and Myanmar"})
        ceo = CEOAgent(llm_client=llm)
        result = await ceo.run_full_day(memory)
        tokens = await memory.total_tokens()
        await update.message.reply_html(
            f"✅ <b>Full agency run complete.</b>\n"
            f"Tokens used: {tokens:,}\n"
            "Each group received their department output.\n"
            "Your CEO brief is above. /pipeline for BD prospects."
        )
    except Exception as exc:
        logger.exception("CEO brief failed: %s", exc)
        await update.message.reply_html(f"❌ Brief failed: {exc}")


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    report = load_latest_report("ceo_daily_report", department="reports/ceo")
    if not report:
        await update.message.reply_html("📭 No report found for today yet. Run /brief to generate one.")
        return
    from utils.telegram import send_ceo_daily_brief
    import datetime
    await send_ceo_daily_brief(report, date=datetime.datetime.now().strftime("%B %d, %Y"))
    await update.message.reply_html("📋 Report sent above.")


async def cmd_research(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    await update.message.reply_html("🔍 <b>Running Market Research...</b>")
    try:
        llm = LLMClient()
        report = await _run_workflow(
            "research_only",
            client_brief={"market": "Singapore and Myanmar"},
            llm=llm,
        )
        result = report.agent_results.get("research_seo")
        if result and result.success:
            keywords = result.data.get("high_intent_keywords", [])
            kw_list = "\n".join(f"• {k.get('keyword', k)}" for k in keywords[:5] if isinstance(k, dict))
            focus = ", ".join(result.data.get("recommended_focus_areas", [])[:3])
            posted = await send_to_marketing_group(result.data)
            group_note = " → Marketing group ✅" if posted else ""
            await update.message.reply_html(
                f"✅ <b>Research complete{group_note}</b>\n\n"
                f"<b>Top keywords:</b>\n{kw_list}\n\n"
                f"<b>Focus areas:</b> {focus}"
            )
        else:
            await update.message.reply_html("❌ Research failed.")
    except Exception as exc:
        await update.message.reply_html(f"❌ Error: {exc}")


async def cmd_bd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """BD pipeline: Research → NOVA. Findings from research flow into prospect selection."""
    if not _security_check(update):
        return
    await update.message.reply_html(
        "📊 <b>NOVA BD Pipeline running...</b>\n\n"
        "Step 1 — Market Research (SG + MM)\n"
        "Step 2 — NOVA picks 3 prospects informed by that research\n\n"
        "~60 seconds."
    )
    try:
        settings = get_settings()
        llm = LLMClient()
        report = await _run_workflow(
            "bd_pipeline",
            client_brief={"market": "Singapore and Myanmar", "agency": "ZYNTH"},
            llm=llm,
        )
        research_result = report.agent_results.get("research_seo")
        lead_result = report.agent_results.get("lead_gen")

        if not lead_result or not lead_result.success:
            await update.message.reply_html("❌ NOVA failed. Try again.")
            return

        prospects = lead_result.data.get("prospects", [])
        _bd_session["prospects"] = prospects
        _bd_session["run_at"] = datetime.now().isoformat()
        _bd_session["full_data"] = lead_result.data

        # Post read-only to BD group
        await send_bd_brief(lead_result.data)
        # Post interactive cards with buttons to personal chat
        await send_bd_brief_interactive(lead_result.data, settings.telegram_chat_id)

        # Show what research context NOVA used
        research_context = ""
        if research_result and research_result.success:
            kws = research_result.data.get("high_intent_keywords", [])
            top = [k.get("keyword", k) if isinstance(k, dict) else k for k in kws[:3]]
            research_context = f"\n<i>Research found: {', '.join(top)}</i>"

        await update.message.reply_html(
            f"✅ <b>NOVA complete — {len(prospects)} prospects above.</b>{research_context}\n\n"
            "Tap ✅ or ⏭ on each card.\n"
            "/pipeline to see your approved prospects."
        )
    except Exception as exc:
        logger.exception("BD pipeline error: %s", exc)
        await update.message.reply_html(f"❌ Error: {exc}")


async def cmd_creative(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Creative pipeline: Research → Copywriter direction → Portfolio executes."""
    if not _security_check(update):
        return
    await update.message.reply_html(
        "🎨 <b>Creative Pipeline running...</b>\n\n"
        "Step 1 — Market Research\n"
        "Step 2 — Copy direction (what content the market needs)\n"
        "Step 3 — Portfolio executes brand brief from that direction\n\n"
        "~60 seconds."
    )
    try:
        llm = LLMClient()
        report = await _run_workflow(
            "creative_pipeline",
            client_brief={"agency": "ZYNTH"},
            llm=llm,
        )
        portfolio_result = report.agent_results.get("portfolio")
        copy_result = report.agent_results.get("copywriter")

        if portfolio_result and portfolio_result.success:
            brand = portfolio_result.data.get("brand", "Unknown")
            tagline = portfolio_result.data.get("creative_direction", {}).get("tagline", "")
            posted = await send_to_creative_group(portfolio_result.data)
            group_note = " → Creative group ✅" if posted else ""

            copy_note = ""
            if copy_result and copy_result.success:
                hook = copy_result.data.get("campaign_concepts", [{}])[0].get("hook", "")
                if hook:
                    copy_note = f"\n<i>Copy hook: {hook[:80]}</i>"

            await update.message.reply_html(
                f"✅ <b>Creative complete{group_note}</b>\n\n"
                f"<b>Brand:</b> {brand}\n"
                f"<b>Tagline:</b> <i>{tagline}</i>"
                f"{copy_note}\n\n"
                "Saved to outputs/portfolio/"
            )
        else:
            err = (portfolio_result.error if portfolio_result else "portfolio step did not run") or "unknown"
            await update.message.reply_html(
                f"❌ Creative pipeline failed: <i>{err[:300]}</i>\n\n"
                "Try /creative again — if it keeps failing, send me this message."
            )
    except Exception as exc:
        await update.message.reply_html(f"❌ Error: {exc}")


async def handle_bd_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle approve/skip/contacted button taps on BD prospect cards."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""

    if data.startswith("bd_contacted_"):
        # Fired from /pipeline — company name is the payload
        company = data[len("bd_contacted_"):]
        mark_contacted(company)
        await query.edit_message_text(
            f"🔵 <b>{company} marked as contacted.</b>\n"
            "Following up later? Send /pipeline.",
            parse_mode="HTML",
        )
        return

    if data.startswith("bd_approve_"):
        idx = int(data[len("bd_approve_"):])
        action = "approve"
    elif data.startswith("bd_skip_"):
        idx = int(data[len("bd_skip_"):])
        action = "skip"
    else:
        return

    prospects = _bd_session.get("prospects", [])
    if idx >= len(prospects):
        await query.edit_message_text("⚠️ Session expired. Run /bd again.")
        return

    prospect = prospects[idx]
    company = prospect.get("company", "Unknown")

    if action == "approve":
        approve_prospect(prospect)
        await query.edit_message_text(
            f"✅ <b>{company} approved!</b>\n"
            "Added to BD pipeline → /pipeline to track progress.",
            parse_mode="HTML",
        )
    else:
        skip_prospect(company)
        await query.edit_message_text(
            f"⏭ <b>{company} skipped.</b>",
            parse_mode="HTML",
        )


async def cmd_pipeline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the BD approval pipeline with pending prospects."""
    if not _security_check(update):
        return

    pending = get_pending()
    all_data = get_all()
    contacted = [p for p in all_data.get("approved", []) if p.get("status") == "contacted"]
    won = [p for p in all_data.get("approved", []) if p.get("status") == "closed_won"]

    if not pending and not contacted and not won:
        await update.message.reply_html(
            "📋 <b>BD Pipeline is empty.</b>\n\n"
            "Run /bd to find prospects and approve them."
        )
        return

    lines = [
        "📋 <b>BD Pipeline</b>",
        "",
        f"🟡 Pending outreach: {len(pending)}",
        f"🔵 Contacted: {len(contacted)}",
        f"🟢 Won: {len(won)}",
        "",
    ]

    if pending:
        lines.append("━━━ <b>Ready for Outreach</b> ━━━")
        for p in pending[:5]:
            company = p.get("company", "?")
            approved_at = p.get("approved_at", "")[:10]
            services = ", ".join(p.get("suggested_services", [])[:2])
            budget = p.get("budget_estimate", "")
            lines.append(
                f"\n🎯 <b>{company}</b>\n"
                f"   {p.get('market', '')} | {services}\n"
                f"   Budget: {budget}\n"
                f"   Approved: {approved_at}"
            )

    await update.message.reply_html("\n".join(lines))

    # Send each pending prospect with a "Mark Contacted" button
    if pending:
        await update.message.reply_html("Tap to update status:")
        for p in pending[:5]:
            company = p.get("company", "?")
            outreach = p.get("outreach_message", "")
            text = (
                f"🎯 <b>{company}</b>\n\n"
                f"📲 Ready to send:\n<code>{outreach[:300]}</code>"
            )
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🔵 Mark as Contacted",
                    callback_data=f"bd_contacted_{company}",
                ),
            ]])
            await update.message.reply_html(text, reply_markup=keyboard)


# ── Event Specialist Team (HITL: approve / revise, max 3 cycles) ─────────────
_event_session: dict = {}
_MAX_EVENT_CYCLES = 3


async def _run_event_cycle(update: Update, brief: str, feedback: str, cycle: int) -> None:
    """One full event-team cycle: 3 specialists + merge → docx → HITL buttons."""
    from agents.event_team import run_event_pipeline
    from utils.docgen import build_proposal_docx
    from utils.cost_tracker import get_cost_tracker

    tracker = await get_cost_tracker()
    sgd_before = (await tracker.today_summary()).get("sgd", 0.0)

    memory = SharedMemory(client_brief={"agency": "ZYNTH", "mode": "event_team"})
    proposal = await _await_with_progress(
        update,
        f"Event team cycle {cycle}/{_MAX_EVENT_CYCLES}: Concept + Design + Ops working in parallel",
        run_event_pipeline(brief, memory, feedback=feedback, cycle=cycle),
    )

    path = build_proposal_docx(
        title=proposal.get("title", "ZYNTH Event Proposal"),
        client=proposal.get("client", "Prospective Client"),
        market=proposal.get("market", ""),
        sections=proposal.get("sections", []),
    )
    sgd_after = (await tracker.today_summary()).get("sgd", 0.0)

    _event_session.update(
        {"brief": brief, "cycle": cycle, "proposal": proposal, "doc_path": str(path), "awaiting_feedback": False}
    )

    caption = (
        f"🎪 {proposal.get('title', 'Event Proposal')}\n"
        f"💰 {proposal.get('estimated_value', '')}\n"
        f"🔄 Cycle {cycle}/{_MAX_EVENT_CYCLES} · cost this cycle ~S${max(sgd_after - sgd_before, 0):.2f}"
    )
    with open(path, "rb") as f:
        await update.message.reply_document(document=f, filename=path.name, caption=caption)

    buttons = [[
        InlineKeyboardButton("✅ Approve & lock", callback_data="evt_approve"),
        InlineKeyboardButton("✏️ Revise", callback_data="evt_revise"),
    ]]
    await update.message.reply_html(
        "Review the document. <b>Approve</b> locks this version (and emails it if "
        "email is set up). <b>Revise</b> lets you send feedback for the next cycle.",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def cmd_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Event Specialist Team: /event <brief> → full proposal with HITL loop."""
    if not _security_check(update):
        return
    if not context.args:
        await update.message.reply_html(
            "🎪 <b>Event Specialist Team</b>\n\n"
            "Describe the event in one line — Concept, Design, and Ops/Vendor "
            "specialists work in parallel, then you approve or revise (max 3 cycles).\n\n"
            "<code>/event fintech product launch, Lotte Hotel, 300 pax, November, premium feel</code>\n"
            "<code>/event IGNITE sponsor gala dinner 400 pax Sedona</code>"
        )
        return
    brief = " ".join(context.args)
    try:
        await _run_event_cycle(update, brief, feedback="", cycle=1)
    except Exception as exc:
        logger.exception("Event pipeline failed: %s", exc)
        await update.message.reply_html(f"❌ Event team failed: {exc}")


async def handle_event_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Approve / Revise buttons on event proposals."""
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    proposal = _event_session.get("proposal")
    if not proposal:
        await query.edit_message_text("Session expired — run /event again.")
        return

    if data == "evt_approve":
        _event_session["awaiting_feedback"] = False
        blender = proposal.get("blender_block", "")
        await query.edit_message_text(
            f"✅ APPROVED — {proposal.get('title', 'proposal')} (cycle {proposal.get('cycle', 1)}) is locked.\n"
            "Next steps: send to client from your inbox · confirm venue/vendor rates (RFQ) "
            "· collect the 50% deposit before any work starts.",
        )
        from utils.mailer import send_email
        from pathlib import Path as _P
        doc = _event_session.get("doc_path")
        if doc and await send_email(
            subject=f"APPROVED event proposal: {proposal.get('title', '')}",
            body=f"Approved at cycle {proposal.get('cycle', 1)}.\nBrief: {_event_session.get('brief', '')}",
            attachments=[_P(doc)],
        ):
            await query.message.reply_html("📧 Approved document emailed to you.")
        if blender:
            await query.message.reply_html(
                "🧊 <b>3D preview block</b> — paste this into Claude Desktop (with Blender MCP) "
                "to render the stage:"
            )
            await query.message.reply_text(blender[:4000])
        return

    if data == "evt_revise":
        cycle = _event_session.get("cycle", 1)
        if cycle >= _MAX_EVENT_CYCLES:
            await query.edit_message_text(
                f"⛔ Max {_MAX_EVENT_CYCLES} cycles reached. Approve this version or "
                "start fresh with a sharper /event brief (cheaper than endless revision)."
            )
            return
        _event_session["awaiting_feedback"] = True
        await query.edit_message_text(
            f"✏️ Revision cycle {cycle + 1}/{_MAX_EVENT_CYCLES} — send your feedback as a "
            "normal message now (what to change, what to keep)."
        )


async def cmd_ops(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    await update.message.reply_html("⚙️ Running Operations & Vendor Research...")
    try:
        from agents.operations import OperationsAgent
        llm = LLMClient()
        memory = SharedMemory()
        agent = OperationsAgent(llm_client=llm)
        result = await agent.run(memory)
        if result.success:
            vendors = result.data.get("vendor_research", [])
            sop = result.data.get("sop_produced", {})
            lines = ["✅ <b>Operations update!</b>\n", f"SOP created: <b>{sop.get('title', 'N/A')}</b>\n", "Vendors researched:"]
            for v in vendors[:3]:
                lines.append(f"• {v.get('vendor_name')} ({v.get('category')}): {v.get('est_price_range')}")
            lines.append("\nSaved to outputs/operations/")
            await update.message.reply_html("\n".join(lines))
        else:
            await update.message.reply_html(f"❌ Ops failed: {result.error}")
    except Exception as exc:
        await update.message.reply_html(f"❌ Error: {exc}")


async def cmd_run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    workflow = " ".join(context.args) if context.args else "full_campaign"
    if workflow not in WORKFLOWS:
        await update.message.reply_html(f"❌ Unknown workflow '{workflow}'. Try: {', '.join(WORKFLOWS.keys())}")
        return

    await update.message.reply_html(f"▶️ Running workflow: <b>{workflow}</b>...")
    try:
        report = await _run_workflow(workflow, client_brief={"agency": "ZYNTH"})
        succeeded = sum(1 for r in report.agent_results.values() if r.success)
        total = len(report.agent_results)
        await update.message.reply_html(
            f"✅ <b>{workflow} complete!</b>\n"
            f"Agents: {succeeded}/{total} succeeded\n"
            f"Tokens used: {report.total_tokens:,}\n"
            f"Status: {report.status}"
        )
    except Exception as exc:
        await update.message.reply_html(f"❌ Workflow failed: {exc}")


async def cmd_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    report = load_latest_report("ceo_daily_report", department="reports/ceo")
    if not report:
        await update.message.reply_html("📭 No action items to approve. Run /brief first.")
        return
    items = report.get("action_items", [])
    if not items:
        await update.message.reply_html("✅ No pending action items in today's report.")
        return
    lines = ["✅ <b>Action items approved!</b> The team will proceed:\n"]
    for item in items:
        lines.append(f"• [{item.get('assigned_to')}] {item.get('item')} → due {item.get('due')}")
    await update.message.reply_html("\n".join(lines))


async def cmd_cost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show today's API cost vs daily budget."""
    if not _security_check(update):
        return
    try:
        from utils.cost_tracker import get_cost_tracker
        tracker = await get_cost_tracker()
        cost = await tracker.today_summary()
        sgd = cost.get("sgd", 0.0)
        usd = cost.get("usd", 0.0)
        calls = cost.get("calls", 0)
        budget = tracker.daily_budget_sgd
        pct = sgd / budget * 100 if budget else 0
        bar_filled = int(pct / 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        status = "🟢" if pct < 80 else ("🟡" if pct < 100 else "🔴")
        await update.message.reply_html(
            f"💰 <b>API Cost Today — {cost.get('date', 'N/A')}</b>\n\n"
            f"{status} [{bar}] {pct:.0f}%\n"
            f"S${sgd:.3f} / S${budget:.0f} budget\n"
            f"US${usd:.4f} | {calls} API calls\n\n"
            "Budget resets at midnight Yangon time."
        )
    except Exception as exc:
        await update.message.reply_html(f"❌ Cost tracker error: {exc}")


async def cmd_proposals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show proposal pool stats and optionally filter by industry."""
    if not _security_check(update):
        return
    from utils.proposal_pool import ProposalPool
    pool = ProposalPool()
    stats = pool.get_stats()
    total = stats.get("total", 0)

    if total == 0:
        await update.message.reply_html(
            "📂 <b>Proposal Pool is empty.</b>\n\n"
            "Run /generate to start building the library.\n"
            "Example: /generate banking january mm"
        )
        return

    industry_filter = " ".join(context.args).strip() if context.args else None

    if industry_filter:
        # Show proposals for a specific industry
        entries = pool.search(industry=industry_filter, limit=8)
        if not entries:
            await update.message.reply_html(f"❌ No proposals found for '{industry_filter}'.")
            return
        lines = [f"📂 <b>Proposals — {industry_filter.title()}</b>\n"]
        for e in entries:
            lines.append(
                f"• <b>{e['title']}</b>\n"
                f"  {e['type']} | {e['month']} | {e['market']}"
            )
        await update.message.reply_html("\n".join(lines))
        return

    # Overall stats
    by_industry = stats.get("by_industry", {})
    by_market = stats.get("by_market", {})
    by_month = stats.get("by_month", {})

    ind_lines = "\n".join(
        f"  • {ind}: {cnt}" for ind, cnt in list(by_industry.items())[:8]
    )
    market_summary = " | ".join(f"{mk}: {cnt}" for mk, cnt in by_market.items())

    covered_months = sorted(by_month.keys(), key=lambda m: MONTHS.index(m) if m in MONTHS else 99)
    month_summary = ", ".join(covered_months[:6]) + ("..." if len(covered_months) > 6 else "")

    await update.message.reply_html(
        f"📂 <b>Proposal Pool — {total} proposals</b>\n\n"
        f"Markets: {market_summary}\n"
        f"Months covered: {month_summary}\n\n"
        f"<b>Top industries:</b>\n{ind_lines}\n\n"
        "Filter: /proposals banking\n"
        "Add more: /generate"
    )


async def _await_with_progress(update: Update, label: str, coro):
    """Run a long task while keeping the user informed via one live status message.

    Edits the same Telegram message every ~25s with elapsed time so long
    generations never look frozen. Deletes the status message when done.
    """
    msg = await update.message.reply_html(f"⏳ <b>{label}</b>\nStarting…")
    task = asyncio.create_task(coro)
    start = time.monotonic()
    try:
        while True:
            done, _ = await asyncio.wait({task}, timeout=25)
            if done:
                break
            elapsed = int(time.monotonic() - start)
            try:
                await msg.edit_text(
                    f"⏳ <b>{label}</b>\n"
                    f"Still working… {elapsed}s elapsed "
                    f"(a full proposal can take 2-3 minutes — this is normal)",
                    parse_mode="HTML",
                )
            except Exception:  # edit can fail if unchanged/too fast — never fatal
                pass
    finally:
        try:
            await msg.delete()
        except Exception:
            pass
    return await task


async def cmd_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate proposals for an industry × month × market combo and add to pool.

    Usage:
        /generate                        ← auto-picks next uncovered MM combo
        /generate banking                ← Banking & Finance, current month, MM
        /generate banking january        ← specific month, MM
        /generate banking january sg     ← specific combo, SG market
    """
    if not _security_check(update):
        return

    from agents.proposal_factory import ProposalFactoryAgent, INDUSTRIES_MM, INDUSTRIES_SG, MONTHS
    from utils.proposal_pool import ProposalPool

    args = [a.strip() for a in context.args] if context.args else []
    pool = ProposalPool()
    llm = LLMClient()
    memory = SharedMemory(client_brief={"agency": "ZYNTH"})
    agent = ProposalFactoryAgent(llm_client=llm)

    # Parse market
    market = "MM"
    if args and args[-1].upper() in ("MM", "SG"):
        market = args.pop().upper()

    # Parse month
    month = datetime.now().strftime("%B")
    if args and args[-1].title() in MONTHS:
        month = args.pop().title()

    # Parse industry (rest of args = industry keyword)
    industry = None
    industries = INDUSTRIES_MM if market == "MM" else INDUSTRIES_SG
    if args:
        query = " ".join(args).lower()
        industry = next(
            (ind for ind in industries if query in ind.lower()),
            None,
        )
        if not industry:
            await update.message.reply_html(
                f"❌ Industry not found for '<b>{' '.join(args)}</b>'.\n\n"
                f"Available ({market}):\n" +
                "\n".join(f"• {ind}" for ind in industries[:8]) +
                "\n...\n\nType part of the name, e.g. /generate banking"
            )
            return
    else:
        # Auto-pick next uncovered combo
        next_combo = agent.next_uncovered(market, pool)
        if next_combo:
            industry, month = next_combo
        else:
            industry = industries[0]

    market_name = "Myanmar" if market == "MM" else "Singapore"

    try:
        proposals = await _await_with_progress(
            update,
            f"Proposal Factory: {industry} × {month} × {market_name}",
            agent.generate_batch(industry, month, market, memory, pool),
        )
        if not proposals:
            await update.message.reply_html("❌ No proposals generated. Try again.")
            return

        # Send summary of generated proposals
        pool_stats = pool.get_stats()
        lines = [
            f"✅ <b>{len(proposals)} proposals added to pool!</b>",
            f"Industry: {industry} | {month} | {market_name}",
            f"Pool total: {pool_stats['total']} proposals\n",
        ]
        for p in proposals:
            budget = p.get("budget_range", {})
            curr = budget.get("currency", "")
            bmin = int(budget.get("min", 0))
            bmax = int(budget.get("max", 0))
            value = p.get("estimated_value_sgd", 0)
            lines.append(
                f"📋 <b>{p['title']}</b>\n"
                f"   {p.get('type', '?')} | {bmin:,}–{bmax:,} {curr}\n"
                f"   {p.get('timeline_weeks', '?')} weeks | Est. S${int(value):,}\n"
                f"   Services: {', '.join(p.get('zynth_services', [])[:3])}"
            )

        # Send in chunks if needed (avoid Telegram 4096 char limit)
        full_text = "\n\n".join(lines)
        if len(full_text) <= 4000:
            await update.message.reply_html(full_text)
        else:
            header = lines[0] + "\n" + lines[1] + "\n" + lines[2]
            await update.message.reply_html(header)
            for prop_text in lines[3:]:
                await update.message.reply_html(prop_text)

        # Show next suggestion
        next_combo = agent.next_uncovered(market, pool)
        if next_combo:
            next_ind, next_mo = next_combo
            await update.message.reply_html(
                f"💡 Next: /generate {next_ind.split(' ')[0].lower()} {next_mo.lower()} {market.lower()}"
            )

    except Exception as exc:
        logger.exception("Proposal generation failed: %s", exc)
        await update.message.reply_html(f"❌ Generation failed: {exc}")


async def _generate_proposal(update: Update, brief: str) -> None:
    """Shared proposal generation: brief → docx → Telegram + email."""
    from agents.master_proposal import MasterProposalAgent
    from utils.docgen import build_proposal_docx
    from utils.cost_tracker import get_cost_tracker

    tracker = await get_cost_tracker()
    sgd_before = (await tracker.today_summary()).get("sgd", 0.0)

    memory = SharedMemory(client_brief={"agency": "ZYNTH", "mode": "master_proposal"})
    agent = MasterProposalAgent(llm_client=LLMClient())

    try:
        data = await _await_with_progress(
            update,
            f"Writing full IGNITE-standard proposal: {brief[:60]}",
            agent.write_proposal(brief, memory),
        )
        path = build_proposal_docx(
            title=data.get("title", "ZYNTH Proposal"),
            client=data.get("client", "Prospective Client"),
            market=data.get("market", ""),
            sections=data.get("sections", []),
        )
        sgd_after = (await tracker.today_summary()).get("sgd", 0.0)
        caption = f"📄 {data.get('title', 'ZYNTH Proposal')}"
        if data.get("estimated_value"):
            caption += f"\n💰 Estimated value: {data['estimated_value']}"
        caption += f"\n💵 Cost ~S${max(sgd_after - sgd_before, 0):.2f}\n\nSave to Google Drive with one tap 📁"
        with open(path, "rb") as f:
            await update.message.reply_document(document=f, filename=path.name, caption=caption)

        from utils.mailer import send_email
        emailed = await send_email(
            subject=f"ZYNTH Proposal: {data.get('title', 'Untitled')}",
            body=(
                f"Proposal generated from brief: {brief}\n"
                f"Estimated value: {data.get('estimated_value', 'n/a')}\n\n"
                "Document attached. — ZYNTH AI"
            ),
            attachments=[path],
        )
        if emailed:
            await update.message.reply_html("📧 Also sent to your email.")
    except Exception as exc:
        logger.exception("Master proposal failed: %s", exc)
        await update.message.reply_html(f"❌ Proposal failed: {exc}")


# ── Guided proposal wizard (buttons → precise brief) ─────────────────────────
_proposal_wizard: dict = {}

_WIZ_TYPE = [
    ("🎪 Event", "Event"), ("📣 Marketing Campaign", "Marketing Campaign"),
    ("🤝 Sponsorship Pitch", "Sponsorship Pitch"), ("🚀 Product Launch", "Product Launch"),
]
_WIZ_MARKET = [("🇲🇲 Myanmar", "Myanmar"), ("🇸🇬 Singapore", "Singapore")]
_WIZ_SCALE = [
    ("Small (<100 / <S$5k)", "Small"), ("Mid (100-300 / S$5-20k)", "Mid"),
    ("Large (300-800 / S$20-60k)", "Large"), ("Flagship (800+ / S$60k+)", "Flagship"),
]


def _wiz_buttons(options: list[tuple[str, str]], prefix: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(label, callback_data=f"{prefix}{val}")] for label, val in options]
    return InlineKeyboardMarkup(rows)


async def cmd_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Full IGNITE-standard proposal as a Word doc — free text OR guided buttons."""
    if not _security_check(update):
        return
    if context.args:
        await _generate_proposal(update, " ".join(context.args))
        return
    # No args → launch guided wizard for a precise brief
    _proposal_wizard.clear()
    await update.message.reply_html(
        "📄 <b>Proposal Builder</b> — answer 3 quick taps, then one line of detail.\n\n"
        "<b>1/3 · What type?</b>",
        reply_markup=_wiz_buttons(_WIZ_TYPE, "pw_type_"),
    )


async def handle_proposal_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Button steps for the guided proposal builder."""
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    if data.startswith("pw_type_"):
        _proposal_wizard["type"] = data[len("pw_type_"):]
        await query.edit_message_text(
            f"Type: <b>{_proposal_wizard['type']}</b>\n\n<b>2/3 · Which market?</b>",
            parse_mode="HTML", reply_markup=_wiz_buttons(_WIZ_MARKET, "pw_market_"),
        )
    elif data.startswith("pw_market_"):
        _proposal_wizard["market"] = data[len("pw_market_"):]
        await query.edit_message_text(
            f"Type: <b>{_proposal_wizard['type']}</b> · Market: <b>{_proposal_wizard['market']}</b>\n\n"
            "<b>3/3 · What scale?</b>",
            parse_mode="HTML", reply_markup=_wiz_buttons(_WIZ_SCALE, "pw_scale_"),
        )
    elif data.startswith("pw_scale_"):
        _proposal_wizard["scale"] = data[len("pw_scale_"):]
        _proposal_wizard["awaiting_detail"] = True
        await query.edit_message_text(
            f"✅ <b>{_proposal_wizard['type']}</b> · <b>{_proposal_wizard['market']}</b> · "
            f"<b>{_proposal_wizard['scale']}</b>\n\n"
            "Now send one line of detail — client/industry, date, and anything specific:\n"
            "<i>e.g. \"fintech app launch for KBZ, November, premium feel, Lotte Hotel\"</i>",
            parse_mode="HTML",
        )


_VENUE_ADD_SCHEMA = {
    "type": "object",
    "required": ["name", "type", "location"],
    "properties": {
        "name": {"type": "string"},
        "type": {"type": "string", "description": "hotel ballroom / convention / outdoor / park / entertainment"},
        "location": {"type": "string"},
        "capacity": {
            "type": "object",
            "properties": {
                "banquet": {"type": ["integer", "null"]},
                "theatre": {"type": ["integer", "null"]},
                "cocktail": {"type": ["integer", "null"]},
            },
        },
        "sqm": {"type": ["number", "null"]},
        "phone": {"type": ["string", "null"]},
        "email": {"type": ["string", "null"]},
        "sales_contact": {"type": ["string", "null"]},
        "price_signal": {"type": ["string", "null"]},
        "notes": {"type": ["string", "null"]},
    },
}


async def cmd_venue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Yangon venue database.

    /venue                      → list all venues (name + capacity)
    /venue search ballroom 500  → filter by keyword and/or min capacity
    /venue add <free text>      → AI structures it into the database
    /venue outreach Novotel     → draft email requesting event kit + floor plans
    """
    if not _security_check(update):
        return
    from utils.venues import all_venues, search, add_venue, format_venue, outreach_email

    args = list(context.args or [])
    sub = args[0].lower() if args else "list"

    if sub == "add":
        raw = " ".join(args[1:]).strip()
        if not raw:
            await update.message.reply_html(
                "Add a venue in free text — I'll structure it. Example:\n"
                "<code>/venue add Yangon Gallery, event hall in Dagon, banquet 300 "
                "theatre 500, contact Ma Su 09-123456, mid-range pricing</code>"
            )
            return
        llm = LLMClient()
        try:
            data, _ = await llm.complete_json(
                system="Extract venue details into the schema. Unknown fields = null. Do not invent numbers.",
                user_prompt=f"Venue info: {raw}",
                schema=_VENUE_ADD_SCHEMA,
                model=get_settings().fallback_model_name,
            )
        except Exception as exc:
            await update.message.reply_html(f"❌ Couldn't parse that: {exc}")
            return
        add_venue(data)
        await update.message.reply_html(
            f"✅ Added (UNVERIFIED until you confirm with the venue):\n\n{format_venue(data)}"
        )
        return

    if sub == "outreach":
        name_q = " ".join(args[1:]).strip()
        matches = search(name_q) if name_q else []
        venue_name = matches[0]["name"] if matches else (name_q or "the venue")
        email_text = outreach_email(venue_name)
        await update.message.reply_html(
            f"📧 <b>Draft outreach — {venue_name}</b>\n"
            "<i>Copy, adjust, and send from your own inbox (nothing auto-sends):</i>"
        )
        await update.message.reply_text(email_text)
        from utils.mailer import send_email
        if await send_email(
            subject=f"[DRAFT to forward] Venue outreach — {venue_name}",
            body=email_text,
        ):
            await update.message.reply_html("📨 Draft also emailed to you for easy forwarding.")
        return

    # list / search
    if sub == "search":
        args = args[1:]
    min_cap = None
    words = []
    for a in args:
        if a.isdigit():
            min_cap = int(a)
        elif sub != "list" or a != "list":
            words.append(a)
    results = search(" ".join(words), min_capacity=min_cap)
    if not results:
        await update.message.reply_html(
            "No venues matched. Try /venue search ballroom 500 — or /venue add to add one."
        )
        return
    header = f"🏛 <b>Venues ({len(results)}/{len(all_venues())})</b>\n\n"
    cards = [format_venue(v) for v in results[:10]]
    text = header + "\n\n".join(cards)
    for i in range(0, len(text), 4000):
        await update.message.reply_html(text[i : i + 4000])
    if len(results) > 10:
        await update.message.reply_html(f"…and {len(results) - 10} more. Narrow with /venue search <keyword>.")


async def cmd_fx(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show or set the MMK market exchange rates used in every proposal.

    /fx                     → refresh (live if possible) and show current rates
    /fx set usd 4290 4400   → manual update (buy sell)
    """
    if not _security_check(update):
        return
    from utils.fx import get_rates, refresh_rates, set_manual

    args = [a.lower() for a in (context.args or [])]
    if len(args) == 4 and args[0] == "set":
        try:
            cur, buy, sell = args[1].upper(), float(args[2].replace(",", "")), float(args[3].replace(",", ""))
        except ValueError:
            await update.message.reply_html("Usage: <code>/fx set usd 4290 4400</code>")
            return
        data = set_manual(cur, buy, sell)
        await update.message.reply_html(
            f"✅ <b>{cur}/MMK updated</b> — buy {buy:,.0f} · sell {sell:,.0f}\n"
            "All proposals now use this market rate."
        )
        return

    live, data = await refresh_rates()
    lines = [
        f"• <b>{cur}</b>/MMK — buy {v['buy']:,.0f} · sell {v['sell']:,.0f}"
        for cur, v in data.get("rates", {}).items()
    ]
    await update.message.reply_html(
        "💱 <b>MMK Market Rates</b> (proposals use these — never the CBM rate)\n\n"
        + "\n".join(lines)
        + f"\n\nSource: {data.get('source')}\nUpdated: {data.get('updated')}"
        + ("" if live else "\n\n⚠️ Live fetch unavailable — update manually anytime:\n<code>/fx set usd 4290 4400</code>")
    )


async def cmd_kb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show which knowledge files the agents are reading."""
    if not _security_check(update):
        return
    from utils.knowledge import list_knowledge_files, load_knowledge

    files = list_knowledge_files()
    if not files:
        await update.message.reply_html(
            "📚 <b>Knowledge Base is empty.</b>\n\n"
            "Add Markdown files to <code>backend/knowledge/</code> on GitHub "
            "and the agents will use them automatically after redeploy."
        )
        return

    lines = ["📚 <b>ZYNTH Knowledge Base</b>\n"]
    active_count = 0
    for name, size, active in files:
        if name.lower() == "readme.md":
            continue
        if active:
            active_count += 1
            lines.append(f"✅ <code>{name}</code> — {size:,} bytes")
        else:
            lines.append(f"⬜ <code>{name}</code> — template not filled yet")

    block = load_knowledge(force=True)
    lines.append(
        f"\n{active_count} file(s) active — {len(block):,} chars injected into every agent."
        if block
        else "\nNo active files yet — fill a template (delete the TEMPLATE marker) to activate it."
    )
    await update.message.reply_html("\n".join(lines))


_CHAT_HISTORY_KEY = "chat_history"
_CHAT_MAX_TURNS = 6  # remember the last 6 exchanges per chat


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Free-text conversation — ask the AI chief of staff anything."""
    if not _security_check(update):
        return
    text = (update.message.text or "").strip()
    if not text:
        return

    # If the proposal wizard is waiting for the detail line, assemble the brief
    if _proposal_wizard.get("awaiting_detail"):
        _proposal_wizard["awaiting_detail"] = False
        brief = (
            f"{_proposal_wizard.get('type', '')} proposal for the "
            f"{_proposal_wizard.get('market', '')} market, "
            f"{_proposal_wizard.get('scale', '')} scale. Details: {text}"
        )
        await _generate_proposal(update, brief)
        return

    # If the MD just hit "Revise" on an event proposal, this message is feedback
    if _event_session.get("awaiting_feedback"):
        _event_session["awaiting_feedback"] = False
        next_cycle = _event_session.get("cycle", 1) + 1
        try:
            await _run_event_cycle(update, _event_session.get("brief", ""), feedback=text, cycle=next_cycle)
        except Exception as exc:
            logger.exception("Event revision failed: %s", exc)
            await update.message.reply_html(f"❌ Revision failed: {exc}")
        return

    await _chat_reply(update, context, text)


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Voice messages: transcribe (Burmese/English via Gemini) then chat."""
    if not _security_check(update):
        return
    voice = update.message.voice or update.message.audio
    if not voice:
        return

    from utils.transcribe import has_transcription, transcribe_voice, TranscriptionError

    if not has_transcription():
        await update.message.reply_html(
            "🎙 <b>Voice needs a one-time (free) setup.</b>\n\n"
            "1. Go to <b>aistudio.google.com/app/apikey</b> → Create API key (free)\n"
            "2. Railway → Variables → add <code>GEMINI_API_KEY</code>\n\n"
            "Then send your voice message again — Burmese and English both work."
        )
        return

    try:
        await update.message.chat.send_action("typing")
        tg_file = await context.bot.get_file(voice.file_id)
        audio = bytes(await tg_file.download_as_bytearray())
        mime = getattr(voice, "mime_type", None) or "audio/ogg"
        text = await transcribe_voice(audio, mime_type=mime)
    except TranscriptionError as exc:
        await update.message.reply_html(f"❌ {exc}")
        return
    except Exception as exc:
        logger.exception("Voice transcription failed: %s", exc)
        await update.message.reply_html("❌ Couldn't transcribe that voice message — check the logs.")
        return

    if not text:
        await update.message.reply_html("🎙 I couldn't hear anything in that clip — try again?")
        return

    await update.message.reply_html(f"🎙 <i>{text}</i>")
    await _chat_reply(update, context, text)


async def _chat_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Shared chat brain: knowledge + today's report + short history → reply.

    Every reply goes through the same daily cost guard as agent runs.
    """
    from config import ZYNTH_BRAND
    from utils.knowledge import load_knowledge

    llm = LLMClient()
    if llm.is_mocked:
        await update.message.reply_html(
            "🔵 Chat needs a live ANTHROPIC_API_KEY (currently in mock mode).\n"
            "Commands like /status still work."
        )
        return

    await update.message.chat.send_action("typing")

    # --- Assemble context: brand + knowledge + today's report + IGNITE ---
    system = (
        f"{ZYNTH_BRAND.as_system_prompt_block()}\n\n"
        "Your specific role: You are the AI Chief of Staff for ZYNTH's founder. "
        "You run their AI agency team (CEO, CMO, BD, Proposal Factory and more, "
        "available via bot commands). Answer questions about the business, brainstorm, "
        "draft messages, and advise on strategy. Be direct, practical, and concise — "
        "this is a Telegram chat, so keep replies short unless asked for detail. "
        "Reply in the language the founder writes in (Burmese or English). "
        "When a bot command would do the job better, mention it "
        "(e.g. /generate for proposals, /bd for prospects, /brief for a full day run)."
    )
    knowledge = load_knowledge()
    if knowledge:
        system += knowledge

    from utils.fx import rates_block
    system += rates_block()

    ignite_line = CEOAgent._ignite_countdown()
    if ignite_line:
        system += f"\n\nToday's context: {ignite_line}"

    report = load_latest_report("ceo_daily_report", department="reports/ceo")
    if report:
        summary = str(report.get("executive_summary", ""))[:600]
        if summary:
            system += f"\n\nLatest CEO daily report summary: {summary}"

    # --- Short per-chat conversation memory ---
    history: list[tuple[str, str]] = context.chat_data.setdefault(_CHAT_HISTORY_KEY, [])
    transcript = "".join(f"\n{who}: {msg}" for who, msg in history)
    prompt = (
        f"Conversation so far:{transcript}\nFounder: {text}\n\n"
        "Reply as the AI Chief of Staff."
        if history
        else text
    )

    try:
        response = await llm.complete(system=system, user_prompt=prompt, max_tokens=1024)
    except Exception as exc:
        logger.exception("Chat reply failed: %s", exc)
        await update.message.reply_html(f"❌ Couldn't reply: {exc}")
        return

    reply = response.text.strip() or "…"
    history.append(("Founder", text[:500]))
    history.append(("Chief of Staff", reply[:500]))
    del history[: max(0, len(history) - _CHAT_MAX_TURNS * 2)]

    # Telegram messages cap at 4096 chars — send in plain-text chunks
    for i in range(0, len(reply), 4000):
        await update.message.reply_text(reply[i : i + 4000])


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = _get_application()
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("start", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("brief", cmd_brief))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("bd", cmd_bd))
    app.add_handler(CommandHandler("pipeline", cmd_pipeline))
    app.add_handler(CommandHandler("creative", cmd_creative))
    app.add_handler(CommandHandler("research", cmd_research))
    app.add_handler(CommandHandler("event", cmd_event))
    app.add_handler(CommandHandler("ops", cmd_ops))
    app.add_handler(CommandHandler("run", cmd_run))
    app.add_handler(CommandHandler("approve", cmd_approve))
    app.add_handler(CommandHandler("cost", cmd_cost))
    app.add_handler(CommandHandler("proposals", cmd_proposals))
    app.add_handler(CommandHandler("generate", cmd_generate))
    app.add_handler(CommandHandler("proposal", cmd_proposal))
    app.add_handler(CommandHandler("fx", cmd_fx))
    app.add_handler(CommandHandler("venue", cmd_venue))
    app.add_handler(CommandHandler("kb", cmd_kb))
    app.add_handler(CallbackQueryHandler(handle_bd_callback, pattern="^bd_"))
    app.add_handler(CallbackQueryHandler(handle_event_callback, pattern="^evt_"))
    app.add_handler(CallbackQueryHandler(handle_proposal_wizard, pattern="^pw_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, voice_handler))

    logger.info("ZYNTH Telegram Bot starting…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
