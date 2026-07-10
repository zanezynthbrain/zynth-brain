"""ZYNTH Telegram Bot — your AI agency in your pocket.

Commands you can send from your iPad/phone:

    /brief          → Run the full daily CEO brief right now
    /status         → Get a quick status of what's running
    /report         → Show yesterday's CEO report
    /creative       → Run just the Portfolio agent (get today's creative work)
    /research       → Run just the Market Research agent
    /event          → Generate a new event proposal
    /ops            → Run Operations (vendor research + SOP)
    /run <workflow> → Run a specific workflow (full_campaign, research_only, etc.)
    /approve        → Approve the latest action items from CEO
    /help           → Show all commands

Setup:
    1. Create bot: message @BotFather on Telegram → /newbot → save token
    2. Get your chat ID: start your bot, then visit:
       https://api.telegram.org/bot<TOKEN>/getUpdates
    3. Add to .env:
       TELEGRAM_BOT_TOKEN=...
       TELEGRAM_CHAT_ID=...
    4. Run: python telegram_bot.py

တည်ဆောက်နည်း:
    Telegram မှာ @BotFather ကို message ပေး → /newbot → token ရမယ်
    .env ထဲ TELEGRAM_BOT_TOKEN ထည့် → python telegram_bot.py run လုပ်
"""

from __future__ import annotations

import asyncio
import json
import sys

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from agents import build_default_agents, OrchestratorAgent, WORKFLOWS
from agents.ceo import CEOAgent
from config import get_settings
from utils.logging_config import configure_logging, get_logger
from utils.llm_client import LLMClient
from utils.state import SharedMemory
from utils.storage import load_latest_report
from utils.telegram import (
    send_message,
    send_bd_brief,
    send_to_creative_group,
    send_to_marketing_group,
    send_to_gm_group,
)

logger = get_logger("telegram_bot")


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
    text = (
        "🧠 <b>ZYNTH AI Agency Bot</b>\n\n"
        "<b>Daily Operations:</b>\n"
        "/brief — Run CEO daily brief (all departments)\n"
        "/status — Current system status\n"
        "/report — Load today's saved CEO report\n\n"
        "<b>Department Commands:</b>\n"
        "/creative — Creative brief → posts to Creative group\n"
        "/research — Market intel → posts to Marketing group\n"
        "/bd — BD outreach brief → posts to BD group\n"
        "/event — Generate event proposal\n"
        "/ops — Vendor research + SOP\n\n"
        "<b>Workflows:</b>\n"
        "/run full_campaign\n"
        "/run research_only\n"
        "/run ads_only\n"
        "/run leads_only\n\n"
        "<b>Management:</b>\n"
        "/approve — Confirm today's action items\n"
        "/help — This message"
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
    if not _security_check(update):
        return
    await update.message.reply_html("📊 Running BD Lead Gen agent...")
    try:
        from agents.lead_gen import LeadGenOutreachAgent
        llm = LLMClient()
        memory = SharedMemory(client_brief={"market": "Myanmar", "agency": "ZYNTH"})
        agent = LeadGenOutreachAgent(llm_client=llm)
        result = await agent.run(memory)
        if result.success:
            prospects = result.data.get("prospect_list", [])
            posted = await send_bd_brief(result.data)
            group_note = " Posted to BD group ✅" if posted else ""
            companies = ", ".join(p.get("company", "?") for p in prospects[:3])
            await update.message.reply_html(
                f"✅ <b>BD Brief ready!</b>\n\n"
                f"🎯 Top targets: {companies}\n"
                f"📲 Cold emails drafted: {len(result.data.get('cold_emails', []))}"
                f"{group_note}"
            )
        else:
            await update.message.reply_html(f"❌ BD agent failed: {result.error}")
    except Exception as exc:
        await update.message.reply_html(f"❌ Error: {exc}")


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
    app.add_handler(CommandHandler("creative", cmd_creative))
    app.add_handler(CommandHandler("research", cmd_research))
    app.add_handler(CommandHandler("bd", cmd_bd))
    app.add_handler(CommandHandler("event", cmd_event))
    app.add_handler(CommandHandler("ops", cmd_ops))
    app.add_handler(CommandHandler("run", cmd_run))
    app.add_handler(CommandHandler("approve", cmd_approve))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_handler))

    logger.info("ZYNTH Telegram Bot starting (polling mode)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
