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
    /help           → All commands
"""

from __future__ import annotations

import asyncio
import sys
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

from agents import build_default_agents, OrchestratorAgent, WORKFLOWS
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


def _get_application() -> Application:
    settings = get_settings()
    if not settings.has_telegram:
        raise RuntimeError(
            "Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
        )
    return Application.builder().token(settings.telegram_bot_token).build()


def _security_check(update: Update) -> bool:
    """Only respond to the configured owner chat. Silently ignore everything else."""
    settings = get_settings()
    return str(update.effective_chat.id) == settings.telegram_chat_id


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    pending = len(get_pending())
    pipeline_note = f"\n⚡ {pending} prospect(s) waiting for outreach → /pipeline" if pending else ""
    text = (
        "🧠 <b>ZYNTH AI Agency — Command Center</b>\n\n"
        "<b>BD & Sales:</b>\n"
        "/bd — NOVA runs BD: 3 prospects, approve/skip with buttons\n"
        "/pipeline — Show approved prospects + mark contacted\n\n"
        "<b>Daily Operations:</b>\n"
        "/brief — Full CEO daily brief (all departments)\n"
        "/report — Load today's saved CEO report\n"
        "/status — System status\n\n"
        "<b>Department Agents:</b>\n"
        "/creative — Creative brief → Creative group\n"
        "/research — Market intel → Marketing group\n"
        "/event — Event proposal (Yangon venues)\n"
        "/ops — Vendor research + SOP\n\n"
        "<b>Campaign Workflows:</b>\n"
        "/run full_campaign\n"
        "/run research_only\n"
        "/run ads_only\n"
        "/run leads_only\n\n"
        "<b>Approvals:</b>\n"
        "/approve — Confirm CEO action items\n"
        "/help — This message"
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
    await update.message.reply_html("🚀 <b>Starting CEO Daily Brief...</b>\nAll departments will run. Check back in ~60 seconds.")
    try:
        llm = LLMClient()
        memory = SharedMemory(client_brief={"agency": "ZYNTH", "mode": "daily_brief"})
        ceo = CEOAgent(llm_client=llm)
        await ceo.run_full_day(memory)
        await update.message.reply_html("✅ <b>Daily brief complete!</b>\nCheck your Telegram for the full report.")
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


async def cmd_creative(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    await update.message.reply_html("🎨 Running Creative Portfolio agent...")
    try:
        from agents.portfolio import PortfolioAgent
        llm = LLMClient()
        memory = SharedMemory()
        agent = PortfolioAgent(llm_client=llm)
        result = await agent.run(memory)
        if result.success:
            brand = result.data.get("brand", "Unknown")
            tagline = result.data.get("creative_direction", {}).get("tagline", "")
            posted = await send_to_creative_group(result.data)
            group_note = " Posted to Creative group ✅" if posted else ""
            await update.message.reply_html(
                f"✅ <b>Portfolio piece complete!</b>\n\n"
                f"Brand: <b>{brand}</b>\n"
                f"Tagline: <i>{tagline}</i>\n\n"
                f"Full package saved to outputs/portfolio/{group_note}"
            )
        else:
            await update.message.reply_html(f"❌ Creative agent failed: {result.error}")
    except Exception as exc:
        await update.message.reply_html(f"❌ Error: {exc}")


async def cmd_research(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    await update.message.reply_html("🔍 Running Market Research & SEO agent...")
    try:
        from agents.research_seo import MarketResearchSEOAgent
        llm = LLMClient()
        memory = SharedMemory(client_brief={"industry": "digital marketing Myanmar"})
        agent = MarketResearchSEOAgent(llm_client=llm)
        result = await agent.run(memory)
        if result.success:
            keywords = result.data.get("high_intent_keywords", [])
            kw_list = "\n".join(f"• {k['keyword']}" for k in keywords[:5] if isinstance(k, dict))
            posted = await send_to_marketing_group(result.data)
            group_note = " Posted to Marketing group ✅" if posted else ""
            await update.message.reply_html(
                f"✅ <b>Research complete!</b>\n\n"
                f"Top keywords found:\n{kw_list}\n\n"
                f"Focus areas: {', '.join(result.data.get('recommended_focus_areas', [])[:3])}"
                f"{group_note}"
            )
        else:
            await update.message.reply_html(f"❌ Research failed: {result.error}")
    except Exception as exc:
        await update.message.reply_html(f"❌ Error: {exc}")


async def cmd_bd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Run NOVA BD agent — sends 3 prospects with approve/skip buttons to personal chat."""
    if not _security_check(update):
        return
    await update.message.reply_html(
        "📊 <b>NOVA is running...</b>\n"
        "Finding 3 real prospects for ZYNTH. Takes ~30 seconds."
    )
    try:
        from agents.lead_gen import LeadGenOutreachAgent
        llm = LLMClient()
        memory = SharedMemory(client_brief={"market": "Singapore and Myanmar", "agency": "ZYNTH"})
        agent = LeadGenOutreachAgent(llm_client=llm)
        result = await agent.run(memory)

        if not result.success:
            await update.message.reply_html(f"❌ NOVA failed: {result.error}")
            return

        # Store results for callback handler
        prospects = result.data.get("prospects", [])
        _bd_session["prospects"] = prospects
        _bd_session["run_at"] = datetime.now().isoformat()
        _bd_session["full_data"] = result.data

        settings = get_settings()

        # 1. Send read-only brief to BD group
        await send_bd_brief(result.data)

        # 2. Send interactive version with buttons to personal chat
        await send_bd_brief_interactive(result.data, settings.telegram_chat_id)

        await update.message.reply_html(
            f"✅ <b>NOVA complete — {len(prospects)} prospects ready.</b>\n"
            "Tap ✅ Approve or ⏭ Skip on each one above.\n"
            "Approved prospects → /pipeline"
        )
    except Exception as exc:
        logger.exception("BD agent error: %s", exc)
        await update.message.reply_html(f"❌ Error: {exc}")


async def handle_bd_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle approve/skip button taps on BD prospect cards."""
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("bd_"):
        return

    parts = query.data.split("_")
    action = parts[1]  # approve or skip
    idx = int(parts[2]) if len(parts) > 2 else 0

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
            f"Added to BD pipeline → /pipeline to track progress.",
            parse_mode="HTML",
        )
    elif action == "skip":
        skip_prospect(company)
        await query.edit_message_text(
            f"⏭ <b>{company} skipped.</b>",
            parse_mode="HTML",
        )
    elif action == "contacted":
        mark_contacted(company)
        await query.edit_message_text(
            f"🔵 <b>{company} marked as contacted.</b>\n"
            "Following up later? Send /pipeline.",
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
                    callback_data=f"bd_contacted_{list(get_all()['approved']).index(p) if p in get_all()['approved'] else 0}",
                ),
            ]])
            await update.message.reply_html(text, reply_markup=keyboard)


async def cmd_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    await update.message.reply_html("🎪 Generating event proposal...")
    try:
        from agents.event_manager import EventManagerAgent
        llm = LLMClient()
        memory = SharedMemory(client_brief={"market": "Yangon, Myanmar"})
        agent = EventManagerAgent(llm_client=llm)
        result = await agent.run(memory)
        if result.success:
            proposals = result.data.get("event_proposals", [])
            lines = ["✅ <b>Event Proposals ready!</b>\n"]
            for p in proposals[:2]:
                lines.append(
                    f"🎪 <b>{p.get('name')}</b>\n"
                    f"   Venue: {p.get('proposed_venue')}\n"
                    f"   Budget: {p.get('est_budget_mmk')}\n"
                    f"   Timeline: {p.get('timeline_weeks')} weeks\n"
                )
            lines.append("\nSaved to outputs/event_management/")
            await update.message.reply_html("\n".join(lines))
        else:
            await update.message.reply_html(f"❌ Event planning failed: {result.error}")
    except Exception as exc:
        await update.message.reply_html(f"❌ Error: {exc}")


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
        agents = build_default_agents()
        orchestrator = OrchestratorAgent(agents=agents)
        report = await orchestrator.run_workflow(
            client_brief={"agency": "ZYNTH"},
            workflow=workflow,
        )
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


async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _security_check(update):
        return
    await update.message.reply_html("Not sure what you mean. Send /help to see all commands.")


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
    app.add_handler(CallbackQueryHandler(handle_bd_callback, pattern="^bd_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_handler))

    logger.info("ZYNTH Telegram Bot starting (polling mode)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
