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

_dashboard_started = False


def _start_dashboard_server() -> None:
    """Serve the live command-center dashboard on $PORT (Railway exposes it).

    Runs a tiny stdlib HTTP server in a daemon thread so it never blocks the
    Telegram polling loop. Re-renders fresh data on every request.
    """
    global _dashboard_started
    if _dashboard_started:
        return
    import json as _json
    import os
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    port = int(os.environ.get("PORT", "8080"))
    token = os.environ.get("ZYNTH_DASHBOARD_TOKEN", "")

    class _Handler(BaseHTTPRequestHandler):
        def _json(self, obj, code=200):
            body = _json.dumps(obj).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            if self.path in ("/health", "/healthz"):
                self.send_response(200); self.end_headers(); self.wfile.write(b"ok"); return
            if self.path.startswith("/api/state"):
                try:
                    from utils.dashboard import build_state
                    self._json(build_state())
                except Exception as exc:
                    self._json({"error": str(exc)}, 500)
                return
            try:
                from utils.dashboard import render_spa
                html = render_spa().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(html)
            except Exception as exc:  # never crash the server
                self.send_response(500); self.end_headers()
                self.wfile.write(f"dashboard error: {exc}".encode())

        def do_POST(self):  # noqa: N802
            if not self.path.startswith("/api/task"):
                self._json({"ok": False}, 404); return
            # optional token guard (only enforced when ZYNTH_DASHBOARD_TOKEN set)
            if token and self.headers.get("X-Token") != token and token not in self.path:
                self._json({"ok": False, "error": "unauthorized"}, 401); return
            try:
                n = int(self.headers.get("Content-Length", 0))
                data = _json.loads(self.rfile.read(n) or b"{}")
                from utils.tasks import add_task, set_status, assign_task
                act = data.get("action")
                if act == "add":
                    add_task(data.get("title", ""), data.get("department", "Operations"), source="dashboard")
                elif act == "status":
                    set_status(data.get("id", ""), data.get("status", ""))
                elif act == "assign":
                    assign_task(data.get("id", ""), data.get("assignee", ""))
                self._json({"ok": True})
            except Exception as exc:
                self._json({"ok": False, "error": str(exc)}, 500)

        def log_message(self, *args):  # silence access logs
            pass

    def _serve():
        try:
            ThreadingHTTPServer(("0.0.0.0", port), _Handler).serve_forever()
        except Exception as exc:
            logger.warning("Dashboard server failed to start: %s", exc)

    threading.Thread(target=_serve, daemon=True).start()
    _dashboard_started = True
    logger.info("Dashboard server listening on :%d", port)


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
    _start_dashboard_server()  # live web dashboard on $PORT
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
        "/video &lt;brief&gt; — Video package: concept + EN/MM script + storyboard + MMK budget 🎬\n"
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
        "<b>Command Center:</b>\n"
        "/dashboard — Live interactive dashboard (departments, tasks, activity)\n"
        "/task — Tasks by department (/task add · list · done) — synced to dashboard\n"
        "/status — Activation checklist (what's live / needs a key)\n\n"
        "<b>Databases (collect real data daily):</b>\n"
        "/prospects — Myanmar business prospects (potential clients, daily)\n"
        "/scout — Research a fresh batch now (/scout fintech)\n"
        "/export — Prospects → CSV (open in Sheets/Excel)\n"
        "/sync — Push prospects to Google Sheets / HubSpot\n"
        "/lead — Client leads &amp; BD pipeline (/lead add · list · stage)\n"
        "/vendor — Supplier database, all categories (/vendor add · search)\n"
        "/venue — Yangon venue DB (search · add · outreach)\n\n"
        "<b>Run the Agency (playbook):</b>\n"
        "/audit — Week 0 Honest Audit: find your starting line\n"
        "/scorecard — 12-metric master scorecard (/scorecard set mrr 12000)\n\n"
        "<b>Knowledge Base:</b>\n"
        "/note — Quick-capture a note to the vault (agents use it instantly)\n"
        "/mirror — Refresh the Obsidian vault (Home · Snapshot · Hot Prospects)\n"
        "/kb — Which business knowledge files the agents are using\n"
        "/fx — MMK market rates used in every proposal (/fx set usd 4290 4400)\n\n"
        "<b>Approvals:</b>\n"
        "/approve — Confirm CEO action items\n"
        "/help — This message\n\n"
        "💬 <i>Or just type anything — your AI Chief of Staff will answer.</i>\n"
        "🎙 <i>Voice messages work too — Burmese and English.</i>"
        f"{pipeline_note}"
    )
    await update.message.reply_html(text)


async def cmd_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the live command-center dashboard (HTML) + the live URL if exposed."""
    if not _security_check(update):
        return
    import os
    from pathlib import Path as _P
    from utils.dashboard import render_dashboard

    await update.message.reply_html("🧠 Building your command center…")
    try:
        html = render_dashboard()
        path = _P("outputs/zynth_dashboard.html")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
        caption = "🧠 <b>ZYNTH Command Center</b> — open in any browser."
        if domain:
            caption += f"\n🌐 Always live: https://{domain}"
        else:
            caption += "\n💡 Expose a public URL in Railway → Settings → Networking to get an always-live link."
        with open(path, "rb") as f:
            await update.message.reply_document(document=f, filename="zynth_dashboard.html", caption=caption)
    except Exception as exc:
        logger.exception("Dashboard failed: %s", exc)
        await update.message.reply_html(f"❌ Dashboard failed: {exc}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Activation dashboard — what's live, what still needs a key, at a glance."""
    if not _security_check(update):
        return
    settings = get_settings()
    llm = LLMClient()

    def row(ok: bool, name: str, live: str, todo: str) -> str:
        return f"{'✅' if ok else '⚠️'} <b>{name}</b> — {live if ok else todo}"

    # Live checks
    llm_ok = not llm.is_mocked
    email_ok = bool(settings.smtp_user and settings.smtp_password)
    voice_ok = bool(settings.gemini_api_key)
    try:
        from utils.knowledge import list_knowledge_files
        kb_active = sum(1 for _, _, a in list_knowledge_files() if a)
    except Exception:
        kb_active = 0
    try:
        from utils.venues import all_venues
        n_venues = len(all_venues())
        n_verified = sum(1 for v in all_venues() if v.get("verified"))
    except Exception:
        n_venues = n_verified = 0
    try:
        from utils.business import get_audit, _load
        audit_done = bool(get_audit().get("completed_at"))
        n_scores = len(_load().get("scorecard", {}))
    except Exception:
        audit_done, n_scores = False, 0
    try:
        from utils.fx import get_rates
        fx = get_rates()
        fx_line = f"{fx.get('source', '?')}"
    except Exception:
        fx_line = "unavailable"

    # Cost today
    try:
        from utils.cost_tracker import get_cost_tracker
        tracker = await get_cost_tracker()
        c = await tracker.today_summary()
        cost_line = f"S${c.get('sgd', 0):.2f} / S${tracker.daily_budget_sgd:.0f} today"
    except Exception:
        cost_line = "n/a"

    core = [
        row(llm_ok, "AI brain (Claude)", "live", "❗ add Anthropic credit → console.anthropic.com"),
        "✅ <b>Telegram</b> — connected",
        row(voice_ok, "Voice (MM/EN)", "on", "add GEMINI_API_KEY in Railway"),
        row(email_ok, "Email delivery", "on", "add SMTP_USER + SMTP_PASSWORD (App Password)"),
    ]
    data = [
        f"📚 <b>Knowledge</b> — {kb_active} active files",
        f"🏛 <b>Venues</b> — {n_venues} ({n_verified} verified{'  ⚠️ verify some!' if n_verified == 0 else ''})",
        f"💱 <b>Market FX</b> — {fx_line}",
        f"📊 <b>Scorecard</b> — {n_scores}/12 set{'  · run /scorecard' if n_scores < 12 else ''}",
        f"🩺 <b>Week 0 Audit</b> — {'done ✅' if audit_done else 'not done — run /audit ❗'}",
    ]
    text = (
        "⚡ <b>ZYNTH — Activation Dashboard</b>\n\n"
        "<b>Core systems</b>\n" + "\n".join(core) +
        "\n\n<b>Business data</b>\n" + "\n".join(data) +
        f"\n\n💵 <b>Cost:</b> {cost_line}\n"
        f"⏰ Brief {settings.daily_brief_hour:02d}:{settings.daily_brief_minute:02d} · "
        f"Proposals 07:00 SGT · Mon/Fri rhythm\n\n"
        "⚠️ = needs one setup step. Send /help for all commands."
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
        one_line_ask=proposal.get("one_line_ask", ""),
        estimated_value=proposal.get("estimated_value", ""),
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
            one_line_ask=data.get("one_line_ask", ""),
            estimated_value=data.get("estimated_value", ""),
        )
        sgd_after = (await tracker.today_summary()).get("sgd", 0.0)
        caption = f"📄 {data.get('title', 'ZYNTH Proposal')}"
        if data.get("estimated_value"):
            caption += f"\n💰 Estimated value: {data['estimated_value']}"
        caption += f"\n💵 Cost ~S${max(sgd_after - sgd_before, 0):.2f}\n\nSave to Google Drive with one tap 📁"
        with open(path, "rb") as f:
            await update.message.reply_document(document=f, filename=path.name, caption=caption)

        from utils.tasks import log_activity
        log_activity("Marketing", f"Proposal generated: {data.get('title','proposal')[:50]}", source="telegram")
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


_audit_session: dict = {}

_AUDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "finance": {"type": "string"},
        "clients": {"type": "string"},
        "operations": {"type": "string"},
        "pipeline": {"type": "string"},
        "starting_line_summary": {"type": "string", "description": "2-3 sentences: honest state of the business and the single most urgent issue"},
        "top_3_priorities": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 3},
    },
}


async def cmd_audit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Week 0 Honest Audit — the playbook's starting line."""
    if not _security_check(update):
        return
    from utils.business import AUDIT_QUESTIONS, get_audit

    prev = get_audit()
    prev_note = f"\n\n<i>(Last done: {prev.get('completed_at')})</i>" if prev.get("completed_at") else ""
    _audit_session["awaiting"] = True
    qs = "\n".join(f"{i}. {q}" for i, q in enumerate(AUDIT_QUESTIONS, 1))
    await update.message.reply_html(
        "🩺 <b>Week 0 — The Honest Audit</b>\n"
        "The playbook's starting line. Answer honestly — lying here only lies to yourself.\n\n"
        f"{qs}\n\n"
        "📝 Reply in ONE message (voice works too) — rough answers are fine. "
        "I'll structure it and give you your starting line."
        f"{prev_note}"
    )


async def _run_audit_capture(update: Update, text: str) -> None:
    from utils.business import save_audit
    from utils.llm_client import LLMClient
    llm = LLMClient()
    try:
        data, _ = await llm.complete_json(
            system="Structure the founder's honest business audit into the schema. Keep their real numbers. Be direct in the starting_line_summary — name the most urgent issue.",
            user_prompt=f"Audit answers: {text}",
            schema=_AUDIT_SCHEMA,
            model=get_settings().fallback_model_name,
        )
    except Exception as exc:
        await update.message.reply_html(f"❌ Couldn't process the audit: {exc}")
        return
    save_audit(data)
    prios = "\n".join(f"{i}. {p}" for i, p in enumerate(data.get("top_3_priorities", []), 1))
    await update.message.reply_html(
        "✅ <b>Audit saved — this is your starting line:</b>\n\n"
        f"{data.get('starting_line_summary', '')}\n\n"
        f"<b>Top priorities:</b>\n{prios}\n\n"
        "Next: Phase 1 (Days 1–30) in docs/playbook/08 — stop the bleeding. "
        "Track progress with /scorecard."
    )
    from utils.mailer import send_email
    await send_email(
        subject="ZYNTH Week 0 Audit — your starting line",
        body=f"{data.get('starting_line_summary','')}\n\nPriorities:\n{prios}\n\nFull answers:\n{text}",
    )


async def _send_long(update: Update, text: str, html: bool = True) -> None:
    """Send a long message split on paragraph/line boundaries (never mid-word)."""
    limit = 3800
    if len(text) <= limit:
        await (update.message.reply_html(text) if html else update.message.reply_text(text))
        return
    chunk = ""
    for para in text.split("\n\n"):
        block = para + "\n\n"
        if len(chunk) + len(block) > limit and chunk:
            await (update.message.reply_html(chunk.rstrip()) if html else update.message.reply_text(chunk.rstrip()))
            chunk = ""
        if len(block) > limit:  # a single huge paragraph — hard-split on lines
            for line in block.split("\n"):
                if len(chunk) + len(line) + 1 > limit and chunk:
                    await (update.message.reply_html(chunk.rstrip()) if html else update.message.reply_text(chunk.rstrip()))
                    chunk = ""
                chunk += line + "\n"
        else:
            chunk += block
    if chunk.strip():
        await (update.message.reply_html(chunk.rstrip()) if html else update.message.reply_text(chunk.rstrip()))


_VENDOR_ADD_SCHEMA = {
    "type": "object",
    "required": ["category", "company"],
    "properties": {
        "category": {"type": "string", "description": "MC/Emcee, DJ/Music, Lighting/AV, Staging, LED, Talent/Models, Catering, Florist/Decor, Photography, Videography, Printing, Fabrication, or other"},
        "company": {"type": "string"},
        "tier": {"type": ["string", "null"], "description": "Premium / Mid / Budget"},
        "best_for": {"type": ["string", "null"]},
        "rate": {"type": ["string", "null"]},
        "lead_time": {"type": ["string", "null"]},
        "contact_person": {"type": ["string", "null"]},
        "phone": {"type": ["string", "null"]},
        "email": {"type": ["string", "null"]},
        "notes": {"type": ["string", "null"]},
    },
}


async def cmd_vendor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Supplier/vendor database — real data for BD and event sourcing.

    /vendor                       → category summary
    /vendor catering              → search a category / keyword
    /vendor add <free text>       → AI structures a new supplier into the DB
    """
    if not _security_check(update):
        return
    from utils.suppliers import search, add_supplier, format_supplier, stats, categories

    args = list(context.args or [])
    sub = args[0].lower() if args else ""

    if sub == "add":
        raw = " ".join(args[1:]).strip()
        if not raw:
            await update.message.reply_html(
                "Add a supplier in free text — I'll structure it:\n"
                "<code>/vendor add Aung Sound, PA + lighting rental Yangon, MMK 800k-3M, "
                "contact Ko Aung 09-771234567, mid-tier, 2 week lead</code>"
            )
            return
        try:
            data, _ = await LLMClient().complete_json(
                system="Extract supplier details into the schema. Keep the founder's real numbers/contacts. Unknown = null.",
                user_prompt=f"Supplier: {raw}",
                schema=_VENDOR_ADD_SCHEMA, model=get_settings().fallback_model_name,
            )
        except Exception as exc:
            await update.message.reply_html(f"❌ Couldn't parse: {exc}")
            return
        add_supplier(data)
        from utils.tasks import log_activity
        log_activity("Events", f"Supplier added: {data.get('company','?')} ({data.get('category','?')})", source="telegram")
        await update.message.reply_html("✅ Added to the supplier database:\n\n" + format_supplier(data))
        return

    if not args:
        await update.message.reply_html(
            "🧰 <b>Supplier / Vendor Database</b>\n\n" + stats() +
            "\n\nSearch: <code>/vendor catering</code> · <code>/vendor LED</code>\n"
            "Add real data: <code>/vendor add ...</code>"
        )
        return

    results = search(" ".join(args))
    if not results:
        await update.message.reply_html(
            "No suppliers matched. Categories:\n" + "\n".join(f"• {c}" for c in categories())
        )
        return
    header = f"🧰 <b>Suppliers ({len(results)})</b>\n\n"
    await _send_long(update, header + "\n\n".join(format_supplier(v) for v in results[:15]))


async def cmd_prospects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Myanmar business prospect database — potential clients, collected daily.

    /prospects                 → stats + hottest prospects
    /prospects bank            → search by keyword / sector
    """
    if not _security_check(update):
        return
    from utils.prospects import stats_text, search, format_prospect, seed_if_empty, all_prospects
    seed_if_empty()
    args = list(context.args or [])
    if not args:
        hot = sorted([p for p in all_prospects() if p.get("fit_score", 0) >= 4],
                     key=lambda p: -p.get("fit_score", 0))[:8]
        body = stats_text()
        if hot:
            body += "\n\n<b>Hottest prospects:</b>\n\n" + "\n\n".join(format_prospect(p) for p in hot)
        await _send_long(
            update,
            "🎯 <b>Myanmar Business Prospects</b>\n\n" + body +
            "\n\nSearch: <code>/prospects telecom</code> · New batch: <code>/scout</code>",
        )
        return
    results = search(" ".join(args))
    if not results:
        await update.message.reply_html(
            "No prospects matched. Try <code>/prospects banking</code> or run <code>/scout</code> to research more."
        )
        return
    await _send_long(update, f"🎯 <b>Prospects ({len(results)})</b>\n\n"
                     + "\n\n".join(format_prospect(p) for p in results[:20]))


async def cmd_scout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Run the Myanmar Market Researcher now — collect a fresh batch of prospects.

    /scout                     → research today's rotating sector
    /scout fintech             → research a specific sector on demand
    """
    if not _security_check(update):
        return
    from scheduler import collect_prospects
    args = list(context.args or [])
    sector = " ".join(args).strip() or None
    label = sector or "today's rotating sector"
    try:
        r = await _await_with_progress(
            update,
            f"🔎 Researching Myanmar businesses: {label}",
            collect_prospects(sector),
        )
    except Exception as exc:
        await update.message.reply_html(f"❌ Research failed: {exc}")
        return
    if r.get("mocked"):
        await update.message.reply_html(
            f"🔎 Seeded {r.get('seeded', 0)} starter prospects (DB: {r['total']}). "
            "Add Anthropic API credit and /scout will research live. See /prospects."
        )
        return
    from utils.prospects import format_prospect
    top = "\n\n".join(format_prospect(p) for p in r["top"]) or "—"
    try:
        from utils.tasks import log_activity
        log_activity("BD", f"/scout +{r['added']} {r['sector']} prospects ({r['total']} total)", source="telegram")
    except Exception:
        pass
    await _send_long(
        update,
        f"🎯 <b>{r['sector']}</b> — +{r['added']} new prospects "
        f"({r['skipped']} dupes skipped). DB now <b>{r['total']}</b>.\n\n"
        f"<b>Top new:</b>\n\n{top}\n\nView all: /prospects",
    )


async def cmd_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Full video production package: concept + bilingual script + storyboard +
    MMK budget + post-production guide → Word doc.

    /video <brief>            → commercial package
    /video tiktok <brief>     → social / 9:16 package
    """
    if not _security_check(update):
        return
    from agents.video_team import run_video_pipeline, package_to_sections
    from utils.docgen import build_proposal_docx
    from utils.cost_tracker import get_cost_tracker

    brief = " ".join(context.args or []).strip()
    if not brief:
        await update.message.reply_html(
            "🎬 <b>Video Production Package</b>\n\n"
            "Give me a brief:\n"
            "<code>/video 30s launch film for WavePay Premium, aspirational, Yangon</code>\n"
            "<code>/video tiktok 15s hook for a bubble-tea brand, Gen-Z</code>\n\n"
            "You get: concept + EN/Myanmar script + storyboard + MMK budget + "
            "post-production guide (Resolve/Premiere/AE/CapCut) as a Word doc.\n"
            "For rendered storyboard frames + deep how-to, just ask me in chat."
        )
        return
    low = brief.lower()
    scale = ("tiktok" if any(k in low for k in ("tiktok", "reel", "short", "9:16", "social"))
             else "brand film" if "brand film" in low else "commercial")
    tracker = await get_cost_tracker()
    before = (await tracker.today_summary()).get("sgd", 0.0)
    memory = SharedMemory(client_brief={"agency": "ZYNTH", "mode": "video"})
    try:
        pkg = await _await_with_progress(
            update, f"🎬 Building video production package ({scale}): {brief[:50]}",
            run_video_pipeline(brief, memory, scale=scale),
        )
    except Exception as exc:
        await update.message.reply_html(f"❌ Video pipeline failed: {exc}")
        return
    path = build_proposal_docx(
        title=pkg.get("title", "ZYNTH Video Production Package"),
        client=pkg.get("client", "Prospective Client"),
        market=pkg.get("market", "Myanmar"),
        sections=package_to_sections(pkg),
        one_line_ask=pkg.get("one_line_ask", ""),
        estimated_value=pkg.get("estimated_value", ""),
    )
    after = (await tracker.today_summary()).get("sgd", 0.0)
    try:
        from utils.tasks import log_activity
        log_activity("Creative", f"Video package: {pkg.get('title', '')[:50]}", source="telegram")
    except Exception:
        pass
    with open(path, "rb") as f:
        await update.message.reply_document(
            document=f, filename=path.name,
            caption=(f"🎬 {pkg.get('title', 'Video Package')} · {scale}\n"
                     f"Budget: {pkg.get('estimated_value', '—')} · cost ~S${after - before:.2f}\n"
                     "Rendered storyboard frames + deep how-to: ask me in chat."),
        )


async def cmd_mirror(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Refresh the Obsidian vault notes (Home, Snapshot, Hot Prospects, What We Built)."""
    if not _security_check(update):
        return
    from utils import obsidian
    try:
        paths = await asyncio.to_thread(obsidian.full_sync)
    except Exception as exc:
        await update.message.reply_html(f"❌ Mirror failed: {exc}")
        return
    names = ", ".join(p.stem for p in paths) or "—"
    await update.message.reply_html(
        f"🧠 <b>Obsidian vault refreshed</b> ({len(paths)} notes: {names}).\n"
        "It syncs to GitHub via the daily workflow — your Obsidian Git pulls it. "
        "Capture your own with /note."
    )


async def cmd_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export the prospect database to a CSV (open in Google Sheets/Excel)."""
    if not _security_check(update):
        return
    from utils.exporter import prospects_csv
    try:
        path, n = prospects_csv()
    except Exception as exc:
        await update.message.reply_html(f"❌ Export failed: {exc}")
        return
    with open(path, "rb") as f:
        await update.message.reply_document(
            document=f, filename=path.name,
            caption=f"📇 {n} prospects — open in Google Sheets (File → Import) or Excel.",
        )


async def cmd_sync(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Push prospects to the configured external databases (Google Sheets / HubSpot).

    /sync            → push to whatever is configured
    /sync sheets     → Google Sheets only
    /sync hubspot    → HubSpot only
    """
    if not _security_check(update):
        return
    from utils import sheets_sync, hubspot_sync
    which = (context.args[0].lower() if context.args else "all")
    lines = []
    if which in ("all", "sheets"):
        if sheets_sync.is_configured():
            ok, msg = await asyncio.to_thread(sheets_sync.push_prospects)
            lines.append(("✅" if ok else "⚠️") + f" Sheets: {msg}")
        else:
            lines.append("⚪ Sheets: not set up (add GOOGLE_SERVICE_ACCOUNT_JSON + PROSPECTS_SHEET_ID)")
    if which in ("all", "hubspot"):
        if hubspot_sync.is_configured():
            ok, msg = await hubspot_sync.push_prospects()
            lines.append(("✅" if ok else "⚠️") + f" HubSpot: {msg}")
        else:
            lines.append("⚪ HubSpot: not set up (add HUBSPOT_TOKEN)")
    await update.message.reply_html("🔁 <b>Sync</b>\n" + "\n".join(lines) +
                                    "\n\nTip: <code>/export</code> gives a CSV with no setup.")


_LEAD_ADD_SCHEMA = {
    "type": "object",
    "required": ["company"],
    "properties": {
        "company": {"type": "string"},
        "contact_person": {"type": ["string", "null"]},
        "phone": {"type": ["string", "null"]},
        "email": {"type": ["string", "null"]},
        "industry": {"type": ["string", "null"]},
        "market": {"type": ["string", "null"], "description": "Myanmar / Singapore"},
        "source": {"type": ["string", "null"], "description": "how the lead came in"},
        "value_sgd": {"type": ["number", "null"], "description": "estimated deal value in SGD"},
        "next_step": {"type": ["string", "null"]},
        "notes": {"type": ["string", "null"]},
    },
}


async def cmd_lead(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Client leads / BD pipeline — collect real data day by day.

    /lead                         → pipeline summary
    /lead list [stage]            → list leads (optionally by stage)
    /lead add <free text>         → AI structures a new lead
    /lead stage <company> <stage> → move a lead (new/contacted/meeting/proposal/won/lost)
    """
    if not _security_check(update):
        return
    from utils.leads import add_lead, update_stage, search, format_lead, pipeline_stats, STAGES

    args = list(context.args or [])
    sub = args[0].lower() if args else ""

    if sub == "add":
        raw = " ".join(args[1:]).strip()
        if not raw:
            await update.message.reply_html(
                "Add a lead in free text (voice works too):\n"
                "<code>/lead add KBZ Bank, fintech launch enquiry, contact U Aung 09-..., "
                "~S$40k, met at event, next: send proposal</code>"
            )
            return
        try:
            data, _ = await LLMClient().complete_json(
                system="Extract the sales lead into the schema. Keep real names/numbers. Unknown = null.",
                user_prompt=f"Lead: {raw}",
                schema=_LEAD_ADD_SCHEMA, model=get_settings().fallback_model_name,
            )
        except Exception as exc:
            await update.message.reply_html(f"❌ Couldn't parse: {exc}")
            return
        lead_id = add_lead(data)
        from utils.tasks import log_activity
        log_activity("BD", f"Lead added: {data.get('company','?')}", source="telegram")
        await update.message.reply_html(f"✅ Lead saved <i>[{lead_id}]</i>:\n\n{format_lead({**data, 'id': lead_id})}")
        return

    if sub == "stage" and len(args) >= 3:
        target, stage = " ".join(args[1:-1]), args[-1].lower()
        lead = update_stage(target, stage)
        if not lead:
            await update.message.reply_html(f"Couldn't move '{target}'. Stages: {', '.join(STAGES)}")
            return
        await update.message.reply_html(f"✅ {lead['company']} → <b>{stage}</b>")
        return

    if sub == "list":
        stage = args[1].lower() if len(args) > 1 and args[1].lower() in STAGES else None
        results = search(stage=stage)
        if not results:
            await update.message.reply_html("No leads yet. Add one: <code>/lead add ...</code>")
            return
        await _send_long(update, f"📇 <b>Leads ({len(results)})</b>\n\n" + "\n\n".join(format_lead(l) for l in results[:20]))
        return

    await update.message.reply_html(
        pipeline_stats() +
        "\n\n<code>/lead add ...</code> · <code>/lead list</code> · "
        "<code>/lead stage KBZ proposal</code>"
    )


_TASK_ADD_SCHEMA = {
    "type": "object",
    "required": ["title", "department"],
    "properties": {
        "title": {"type": "string"},
        "department": {"type": "string", "description": "BD, Events, Creative, Marketing, Operations, Finance, or Content"},
        "assignee": {"type": ["string", "null"]},
    },
}


async def cmd_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tasks — shared with the dashboard. /task add · list · done.

    /task add follow up KBZ proposal, BD, assign me
    /task list [department]
    /task done T003
    """
    if not _security_check(update):
        return
    from utils.tasks import add_task, set_status, all_tasks, tasks_by_department, DEPARTMENTS

    args = list(context.args or [])
    sub = args[0].lower() if args else ""

    if sub == "add":
        raw = " ".join(args[1:]).strip()
        if not raw:
            await update.message.reply_html(
                "Add a task (voice works): <code>/task add follow up KBZ proposal, BD</code>"
            )
            return
        try:
            data, _ = await LLMClient().complete_json(
                system="Extract a work task. Pick the department from BD/Events/Creative/Marketing/Operations/Finance/Content.",
                user_prompt=f"Task: {raw}", schema=_TASK_ADD_SCHEMA, model=get_settings().fallback_model_name,
            )
        except Exception:
            data = {"title": raw, "department": "Operations"}
        t = add_task(data.get("title", raw), data.get("department", "Operations"), assignee=data.get("assignee") or "", source="telegram")
        await update.message.reply_html(f"✅ Task <i>[{t['id']}]</i> → <b>{t['department']}</b>\n{t['title']}")
        return

    if sub == "done" and len(args) >= 2:
        t = set_status(args[1], "done")
        await update.message.reply_html(f"✅ Done: {t['title']}" if t else "Task not found.")
        return

    if sub == "list":
        dept = None
        if len(args) > 1:
            from utils.tasks import normalize_dept
            dept = normalize_dept(args[1])
        tbd = tasks_by_department()
        depts = [dept] if dept else DEPARTMENTS
        lines = []
        for d in depts:
            items = [t for t in tbd.get(d, []) if t.get("status") != "done"]
            if items:
                lines.append(f"<b>{d}</b>")
                lines += [f"  • [{t['id']}] {t['title']} <i>({t['status']})</i>" for t in items]
        await update.message.reply_html("\n".join(lines) if lines else "No open tasks. Add with /task add.")
        return

    # summary
    tasks = all_tasks()
    openc = sum(1 for t in tasks if t.get("status") != "done")
    await update.message.reply_html(
        f"📋 <b>Tasks:</b> {openc} open / {len(tasks)} total\n\n"
        "<code>/task add ...</code> · <code>/task list</code> · <code>/task done T001</code>\n"
        "Or manage them visually in /dashboard."
    )


_NOTE_SCHEMA = {
    "type": "object",
    "required": ["title", "category", "body"],
    "properties": {
        "title": {"type": "string", "description": "short filename-safe title"},
        "category": {"type": "string", "description": "clients / projects / events / ideas / market / general"},
        "body": {"type": "string", "description": "the note as clean Markdown, keep the founder's facts"},
    },
}


async def cmd_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Quick-capture a note into the vault — agents use it immediately.

    /note KBZ wants a fintech launch in Nov, budget ~S$40k, contact U Aung
    """
    if not _security_check(update):
        return
    if not context.args:
        await update.message.reply_html(
            "🗒 <b>Quick note → vault</b>\n\n"
            "Send <code>/note &lt;anything&gt;</code> (typing or voice) and I'll file it "
            "so every agent can use it in proposals and briefs.\n\n"
            "<code>/note Meliá sales contact Ma Hnin 09-..., ballroom held for 12 Nov</code>"
        )
        return
    await _capture_note(update, " ".join(context.args))


async def _capture_note(update: Update, text: str) -> None:
    import json as _json
    import re as _re
    from pathlib import Path as _P
    from datetime import datetime as _dt

    llm = LLMClient()
    try:
        data, _ = await llm.complete_json(
            system="File the founder's quick note. Pick a category and a short title. Keep their facts; clean it into Markdown.",
            user_prompt=f"Note: {text}",
            schema=_NOTE_SCHEMA,
            model=get_settings().fallback_model_name,
        )
    except Exception:
        # Even if the model fails, never lose the note — save raw.
        data = {"title": "note", "category": "general", "body": text}

    cat = _re.sub(r"[^a-z]", "", data.get("category", "general").lower()) or "general"
    slug = _re.sub(r"[^\w-]", "_", data.get("title", "note").lower())[:50] or "note"
    stamp = _dt.now().strftime("%Y%m%d_%H%M")
    folder = _P("outputs/proposal_pool/vault") / cat
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{slug}_{stamp}.md"
    path.write_text(
        f"# {data.get('title', 'Note')}\n"
        f"<!-- captured {stamp} via Telegram -->\n\n{data.get('body', text)}\n",
        encoding="utf-8",
    )
    # Refresh the knowledge cache so the note is live right away
    try:
        from utils.knowledge import load_knowledge
        load_knowledge(force=True)
    except Exception:
        pass
    from utils.tasks import log_activity
    log_activity("Content", f"Note filed: {data.get('title','note')}", source="telegram")
    await update.message.reply_html(
        f"🗒 <b>Filed:</b> {data.get('title')}  ·  <i>{cat}</i>\n"
        "Agents can use it now. It's saved to the vault and syncs to the repo."
    )


async def cmd_testemail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Free check that email delivery actually works (no LLM call)."""
    if not _security_check(update):
        return
    from utils.mailer import has_email, send_email
    if not has_email():
        await update.message.reply_html(
            "📧 Email not configured. Add <code>SMTP_USER</code> + "
            "<code>SMTP_PASSWORD</code> (Google App Password) in Railway."
        )
        return
    await update.message.reply_html("📧 Sending a test email…")
    ok = await send_email(
        subject="ZYNTH bot — email test ✅",
        body="If you're reading this, email delivery from your ZYNTH bot works. — ZYNTH AI",
    )
    if ok:
        await update.message.reply_html(
            "✅ <b>Sent.</b> Check your inbox (and spam folder just in case). "
            "Proposals and the weekly briefs will land here too."
        )
    else:
        await update.message.reply_html(
            "❌ <b>Send failed.</b> Usually the App Password: it must be the "
            "16-character Google App Password (no spaces), and 2-Step Verification "
            "must be ON for zane@zynth.asia. Re-check SMTP_PASSWORD in Railway."
        )


async def cmd_scorecard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """The 12-metric agency master scorecard."""
    if not _security_check(update):
        return
    from utils.business import set_metric, scorecard_view

    args = [a.lower() for a in (context.args or [])]
    if len(args) == 3 and args[0] == "set":
        try:
            value = float(args[2].replace(",", "").replace("%", ""))
        except ValueError:
            await update.message.reply_html("Usage: <code>/scorecard set gross_margin 48</code>")
            return
        spec = set_metric(args[1], value)
        if not spec:
            await update.message.reply_html(f"Unknown metric '{args[1]}'. See /scorecard for keys.")
            return
        await update.message.reply_html(f"✅ {spec['label']} = {spec['unit']}{value:g} (target {spec['target']})")
        return
    await update.message.reply_html(scorecard_view())


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

    # If the Week 0 audit is waiting for answers, capture them
    if _audit_session.get("awaiting"):
        _audit_session["awaiting"] = False
        await _run_audit_capture(update, text)
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

    # Telegram caps at 4096 chars — split on paragraph/line boundaries, not mid-word
    await _send_long(update, reply, html=False)


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = _get_application()
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("start", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("dashboard", cmd_dashboard))
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
    app.add_handler(CommandHandler("audit", cmd_audit))
    app.add_handler(CommandHandler("scorecard", cmd_scorecard))
    app.add_handler(CommandHandler("note", cmd_note))
    app.add_handler(CommandHandler("testemail", cmd_testemail))
    app.add_handler(CommandHandler("vendor", cmd_vendor))
    app.add_handler(CommandHandler("lead", cmd_lead))
    app.add_handler(CommandHandler("prospects", cmd_prospects))
    app.add_handler(CommandHandler("scout", cmd_scout))
    app.add_handler(CommandHandler("export", cmd_export))
    app.add_handler(CommandHandler("sync", cmd_sync))
    app.add_handler(CommandHandler("mirror", cmd_mirror))
    app.add_handler(CommandHandler("video", cmd_video))
    app.add_handler(CommandHandler("task", cmd_task))
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
