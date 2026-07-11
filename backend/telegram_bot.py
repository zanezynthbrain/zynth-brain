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
    settings = get_settings()
    scheduler = build_scheduler(settings)
    scheduler.start()
    application.bot_data["scheduler"] = scheduler
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
        "/event — Event proposal (Yangon venues)\n"
        "/ops — Vendor research + SOP\n\n"
        "<b>Campaign Workflows:</b>\n"
        "/run full_campaign\n"
        "/run research_only\n"
        "/run ads_only\n"
        "/run leads_only\n\n"
        "<b>Proposal Factory:</b>\n"
        "/generate — Generate proposals (auto-picks next uncovered combo)\n"
        "/generate banking january mm — Specific industry · month · market\n"
        "/proposals — Browse proposal pool stats\n\n"
        "<b>Knowledge Base:</b>\n"
        "/kb — Which business knowledge files the agents are using\n\n"
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
            await update.message.reply_html("❌ Creative pipeline failed.")
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
    await update.message.reply_html(
        f"🏭 <b>Proposal Factory running...</b>\n\n"
        f"Industry: <b>{industry}</b>\n"
        f"Month: <b>{month}</b>\n"
        f"Market: <b>{market_name}</b>\n\n"
        "Generating 4-5 proposals (~30 sec)..."
    )

    try:
        proposals = await agent.generate_batch(industry, month, market, memory, pool)
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
    app.add_handler(CommandHandler("cost", cmd_cost))
    app.add_handler(CommandHandler("proposals", cmd_proposals))
    app.add_handler(CommandHandler("generate", cmd_generate))
    app.add_handler(CommandHandler("kb", cmd_kb))
    app.add_handler(CallbackQueryHandler(handle_bd_callback, pattern="^bd_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_handler))

    logger.info("ZYNTH Telegram Bot starting…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
