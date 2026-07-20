"""Autonomous daily scheduler for ZYNTH AI Agency.

Runs the CEO Agent on a schedule so the agency works even when you're
sleeping. Uses Yangon timezone (UTC+6:30 / Asia/Rangoon).

Default schedule:
    08:00 Yangon time → Morning CEO Daily Brief (all departments run)
    18:00 Yangon time → End-of-day report summary to Telegram

Run standalone (keep this running on your server/VPS/Raspberry Pi):
    python scheduler.py

Or run via Docker / systemd service so it survives reboots.

ဒီ scheduler ကို server တစ်ခုပေါ်မှာ always-on run ထားရမယ်။
ဥပမာ: Railway, Render, DigitalOcean Droplet, or a Raspberry Pi at home.
ဒါဆို မင်း အိပ်နေချိန်မှာ AI team က အလုပ်လုပ်နေမှာ 😴 → Telegram ပို့မယ်။
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from agents.ceo import CEOAgent
from config import get_settings
from utils.llm_client import LLMClient
from utils.logging_config import configure_logging, get_logger
from utils.state import SharedMemory
from utils.telegram import send_message

logger = get_logger("scheduler")


async def run_morning_brief() -> None:
    """Triggered at configured hour each morning. Runs full CEO daily cycle."""
    today = datetime.now().strftime("%A, %B %d, %Y")
    logger.info("🌅 Morning brief starting: %s", today)
    await send_message(f"🌅 <b>Good morning!</b> ZYNTH AI team starting daily brief for {today}...")

    try:
        llm = LLMClient()
        memory = SharedMemory(client_brief={"agency": "ZYNTH", "mode": "autonomous_daily"})
        ceo = CEOAgent(llm_client=llm)
        await ceo.run_full_day(memory)
        logger.info("Morning brief completed successfully")
    except Exception as exc:
        logger.exception("Morning brief failed: %s", exc)
        await send_message(f"❌ <b>Morning brief failed:</b> {exc}\n\nCheck server logs.")


async def run_eod_report() -> None:
    """Triggered at end of working day. Sends a quick summary of what got done."""
    logger.info("🌙 End-of-day report starting")
    from utils.storage import load_latest_report
    report = load_latest_report("ceo_daily_report", department="reports/ceo")

    if report:
        summary = report.get("executive_summary", "No summary available.")
        tomorrow = report.get("tomorrow_priorities", [])
        tomorrow_text = "\n".join(f"• {p}" for p in tomorrow[:3])
        text = (
            "🌙 <b>ZYNTH End of Day</b>\n\n"
            f"<b>Today's summary:</b>\n{summary}\n\n"
            f"<b>Tomorrow's priorities:</b>\n{tomorrow_text}\n\n"
            "Rest well — the AI team will start fresh tomorrow at 8am 🕗"
        )
    else:
        text = (
            "🌙 <b>ZYNTH End of Day</b>\n\n"
            "No brief was run today. Use /brief in the bot to trigger one, "
            "or check that the scheduler is running correctly."
        )
    await send_message(text)


async def run_weekly_portfolio_review() -> None:
    """Every Monday: review the portfolio pieces produced last week."""
    await send_message(
        "📁 <b>Weekly Portfolio Review</b>\n\n"
        "This week's creative portfolio pieces are saved in outputs/portfolio/\n"
        "Review them and pick your favorites for the ZYNTH website showcase.\n\n"
        "Tip: Ask me /creative to generate a new piece for any brand!"
    )


# ── MD Learning Brief ────────────────────────────────────────────────────────
# One event discipline per week, rotating. Goal: the MD can read a budget,
# a run-of-show, and an AV quote without being fooled.
LEARNING_TOPICS = [
    "Event budgeting: full cost structure of a 200-pax corporate dinner (venue, F&B per pax, AV, staging, staffing, 10% contingency, permits, overtime) and where margins leak",
    "Run-of-show & cue sheets: load-in/load-out windows, soundcheck timing, changeovers, and how to read a production schedule",
    "AV & staging vocabulary: truss, rigging points, LED pixel pitch (P2.6 vs P3.9), projector throw distance, power distribution, dB limits — the negotiating armor",
    "Venue site inspection checklist: capacity by setup, ceiling height, loading access, power, in-house AV exclusivity clauses, corkage",
    "Corporate summit format: agenda design, speaker management, registration flow, sponsor visibility tiers",
    "Product launch events: reveal moments, press handling, demo zones, influencer seeding",
    "Brand activations & roadshows: footfall math, sampling logistics, permits, staffing ratios",
    "Gala dinners & award nights: seating politics, programme pacing, F&B timing with the show",
    "Concerts & live entertainment: artist riders, security ratios, sound limits, ticketing basics",
    "Exhibitions & trade shows: booth economics, floorplan flow, lead capture",
    "Hybrid & livestreamed events: switching, IMAG, platform choice, remote speaker handling",
    "Sustainable staging: modular re-usable builds, material choices, what SG clients now demand",
    "Vendor negotiation: RFQ discipline (3 quotes), deposit terms, cancellation clauses, penalty terms",
    "Event P&L review: post-event reconciliation, actual-vs-budget variance, what to log for next time",
    "Sponsorship packaging: tier design, benefit costing, activation rights — the IGNITE revenue engine",
    "Client-side commercial discipline: change orders in writing, scope creep, the 50% deposit rule in practice",
]


async def run_learning_brief() -> None:
    """Monday morning: teach the MD one event discipline + one regional trend."""
    week = int(datetime.now().strftime("%W"))
    topic = LEARNING_TOPICS[week % len(LEARNING_TOPICS)]
    logger.info("📚 MD Learning Brief: %s", topic[:60])

    from utils.llm_client import LLMClient
    llm = LLMClient()
    system = (
        "You are a veteran SE-Asia event producer (Singapore + Yangon markets) mentoring "
        "a new agency MD. Teach clearly and practically. No fluff. Use real numbers and "
        "local context (Yangon vendor realities, SG client standards). Reply in English "
        "with key terms usable in conversation with vendors."
    )
    prompt = (
        f"This week's lesson: {topic}\n\n"
        "Write a Telegram-friendly brief (~400 words):\n"
        "1. The concept, explained like a mentor on a site visit\n"
        "2. Concrete numbers/benchmarks (Yangon MMK and SG SGD where relevant)\n"
        "3. The 3 mistakes rookies make\n"
        "4. One question the MD should ask a vendor this week to practice\n"
        "5. Finish with ONE current regional creative trend (SG/TH/VN) in 2 sentences."
    )
    try:
        response = await llm.complete(system=system, user_prompt=prompt, max_tokens=1500)
        text = f"📚 <b>MD Learning Brief — Week {week}</b>\n\n{response.text.strip()}"
        await send_message(text[:4000])
        from utils.mailer import send_email
        await send_email(
            subject=f"ZYNTH MD Learning Brief — Week {week}",
            body=f"Topic: {topic}\n\n{response.text.strip()}",
        )
    except Exception as exc:
        logger.exception("Learning brief failed: %s", exc)


async def run_fx_refresh() -> None:
    """Daily: refresh MMK market rates so every proposal prices correctly."""
    from utils.fx import refresh_rates
    live, data = await refresh_rates()
    if not live:
        logger.info("FX refresh: live source unavailable, using %s", data.get("source"))


async def run_consolidation() -> None:
    """Autonomous nightly consolidation — the bot works like a department while
    the MD is away: reviews all the data, organises it, flags what needs
    attention, and reports a digest.
    """
    logger.info("🧩 Nightly consolidation starting")
    try:
        from utils.leads import all_leads
        from utils.suppliers import all_suppliers
        from utils.business import scorecard_view
        from utils.llm_client import LLMClient
        from datetime import datetime as _dt

        leads = all_leads()
        suppliers = all_suppliers()

        # Deterministic facts first (never trust the model for counts)
        stale = [l for l in leads if l.get("stage") not in ("won", "lost")]
        no_contact = [v for v in suppliers if not (v.get("phone") or v.get("email"))]
        unverified_v = [v for v in suppliers if not v.get("verified")]

        llm = LLMClient()
        if llm.is_mocked:
            logger.info("Consolidation skipped — no API key")
            return

        system = (
            "You are ZYNTH's autonomous Operations department doing a nightly review "
            "while the founder sleeps. Be concise, specific, and action-oriented. "
            "No fluff, no restating the numbers you're given — turn them into the 3-5 "
            "things that actually move the business tomorrow."
        )
        prompt = (
            f"Nightly data review for {_dt.now():%A %d %b}.\n\n"
            f"Leads: {len(leads)} total, {len(stale)} open. Stages: "
            f"{[l.get('stage') for l in leads]}.\n"
            f"Open lead details: {[{k: l.get(k) for k in ('company','stage','next_step','value_sgd')} for l in stale][:15]}\n\n"
            f"Suppliers: {len(suppliers)} total, {len(no_contact)} with no contact captured, "
            f"{len(unverified_v)} unverified.\n\n"
            "Produce a short nightly digest for the founder:\n"
            "1. What needs action tomorrow (leads to follow up, by name)\n"
            "2. Data gaps to close (which suppliers/venues need contacts or verification)\n"
            "3. One pattern or opportunity you notice\n"
            "Keep it under 250 words. Address the founder directly."
        )
        resp = await llm.complete(system=system, user_prompt=prompt, max_tokens=900)
        digest = (
            "🧩 <b>Nightly Consolidation</b> — your AI ops team worked while you were away\n\n"
            f"{resp.text.strip()}\n\n"
            f"<i>Snapshot: {len(leads)} leads · {len(suppliers)} suppliers · "
            f"{len(no_contact)} missing contacts</i>"
        )
        await send_message(digest[:4000])
        from utils.mailer import send_email
        await send_email(subject="ZYNTH — nightly consolidation digest", body=resp.text.strip())
    except Exception as exc:
        logger.exception("Consolidation failed: %s", exc)


async def collect_prospects(sector: str | None = None, count: int = 25) -> dict:
    """Core market-research routine, shared by the daily job and the /research
    command. Seeds the DB on first run, researches one sector, dedupe-appends,
    and returns a summary. Never raises for a missing API key (returns mocked).
    """
    from datetime import datetime as _dt
    from utils.prospects import seed_if_empty, add_batch, all_prospects, TARGET_SECTORS

    seeded = seed_if_empty()
    if not sector:
        doy = int(_dt.now().strftime("%j"))
        sector = TARGET_SECTORS[doy % len(TARGET_SECTORS)]

    llm = LLMClient()
    if llm.is_mocked:
        return {"sector": sector, "seeded": seeded, "added": 0, "skipped": 0,
                "total": len(all_prospects()), "top": [], "mocked": True}

    from agents.market_researcher import MarketResearcherAgent
    known = [p.get("company", "") for p in all_prospects()]
    memory = SharedMemory(client_brief={"agency": "ZYNTH", "mode": "market_research"})
    agent = MarketResearcherAgent(llm_client=llm)
    rows = await agent.research_segment(sector, memory, known=known, count=count)
    res = add_batch(rows, source=f"researcher:{sector}")
    top = sorted(rows, key=lambda r: r.get("fit_score", 0), reverse=True)[:5]
    return {"sector": sector, "seeded": seeded, "added": res["added"],
            "skipped": res["skipped"], "total": res["total"], "top": top, "mocked": False}


async def run_market_research() -> None:
    """Daily autonomous Myanmar business researcher — grows the prospect DB and
    reports the day's new potential clients to Telegram + email."""
    logger.info("🔎 Market research starting")
    try:
        r = await collect_prospects()
        if r.get("mocked"):
            if r.get("seeded"):
                await send_message(
                    f"🔎 <b>Market Researcher</b> seeded {r['seeded']} starter prospects. "
                    "Add Anthropic API credit and it will grow the list every day. See /prospects."
                )
            return
        top = "\n".join(
            f"• <b>{p.get('company')}</b> ({p.get('fit_score')}★) — {p.get('why_fit', '')}"
            for p in r["top"]
        ) or "—"
        await send_message(
            (
                f"🔎 <b>Market Researcher — {r['sector']}</b>\n"
                f"+{r['added']} new prospects today · {r['skipped']} dupes skipped · "
                f"DB now <b>{r['total']}</b>\n\n<b>Top new:</b>\n{top}\n\n"
                "All: /prospects · Dig a sector: /research &lt;sector&gt;"
            )[:4000]
        )
        try:
            from utils.tasks import log_activity
            log_activity("BD", f"Market research +{r['added']} {r['sector']} prospects ({r['total']} total)", source="researcher")
        except Exception:
            pass
        from utils.mailer import send_email
        body = (
            f"Sector: {r['sector']}\nAdded: {r['added']} (skipped {r['skipped']} dupes)\n"
            f"Total prospects: {r['total']}\n\nTop new:\n"
            + "\n".join(f"- {p.get('company')} ({p.get('fit_score')}/5): {p.get('why_fit', '')}" for p in r["top"])
        )
        await send_email(subject=f"ZYNTH Market Research — {r['sector']} (+{r['added']})", body=body)
    except Exception as exc:
        logger.exception("Market research failed: %s", exc)


async def run_monday_priorities() -> None:
    """Monday: the playbook's weekly cadence kickoff + scorecard snapshot."""
    from utils.business import scorecard_view
    await send_message(
        "🗓 <b>Monday — Weekly Operating Cadence</b>\n\n"
        "Playbook rhythm for this week:\n"
        "• 09:00 Standup — this week's priorities\n"
        "• Traffic/Resourcing — who works on what\n"
        "• Pipeline Review — deals to push\n\n"
        "Reply with your 3 priorities for the week (I'll remember them).\n\n"
        + scorecard_view()
    )


async def run_friday_review() -> None:
    """Friday: the non-negotiable client update + weekly review nudge."""
    await send_message(
        "🌆 <b>Friday — Weekly Review & Client Updates</b>\n\n"
        "The Speed Moat is non-negotiable:\n"
        "• Send EVERY active client their weekly update (no exception)\n"
        "• Log this week's numbers → /scorecard set ...\n"
        "• Review: what shipped, what slipped, what's at risk\n\n"
        "Agencies die at PROVE + EXPAND. Friday is where you win them."
    )


def build_scheduler(settings=None) -> AsyncIOScheduler:
    settings = settings or get_settings()
    scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)

    # Morning CEO brief
    scheduler.add_job(
        run_morning_brief,
        CronTrigger(
            hour=settings.daily_brief_hour,
            minute=settings.daily_brief_minute,
            timezone=settings.scheduler_timezone,
        ),
        id="morning_brief",
        name="CEO Morning Brief",
        replace_existing=True,
    )

    # End-of-day report
    scheduler.add_job(
        run_eod_report,
        CronTrigger(
            hour=settings.eod_report_hour,
            minute=0,
            timezone=settings.scheduler_timezone,
        ),
        id="eod_report",
        name="End of Day Report",
        replace_existing=True,
    )

    # Weekly portfolio review (Monday 9am Yangon time)
    scheduler.add_job(
        run_weekly_portfolio_review,
        CronTrigger(day_of_week="mon", hour=9, minute=0, timezone=settings.scheduler_timezone),
        id="weekly_portfolio_review",
        name="Weekly Portfolio Review",
        replace_existing=True,
    )

    # MD Learning Brief (Monday 08:30 Yangon = 10:00 SGT)
    scheduler.add_job(
        run_learning_brief,
        CronTrigger(day_of_week="mon", hour=8, minute=30, timezone=settings.scheduler_timezone),
        id="md_learning_brief",
        name="MD Learning Brief",
        replace_existing=True,
    )

    # Daily market FX refresh (07:00 Yangon, before the day's proposals)
    scheduler.add_job(
        run_fx_refresh,
        CronTrigger(hour=7, minute=0, timezone=settings.scheduler_timezone),
        id="fx_refresh",
        name="Market FX Refresh",
        replace_existing=True,
    )

    # Daily Myanmar market research (06:30 Yangon — new prospects before the day)
    scheduler.add_job(
        run_market_research,
        CronTrigger(hour=6, minute=30, timezone=settings.scheduler_timezone),
        id="market_research",
        name="Daily Market Research",
        replace_existing=True,
    )

    # Autonomous nightly consolidation (21:00 Yangon — while the MD is away)
    scheduler.add_job(
        run_consolidation,
        CronTrigger(hour=21, minute=0, timezone=settings.scheduler_timezone),
        id="nightly_consolidation",
        name="Nightly Consolidation",
        replace_existing=True,
    )

    # Weekly operating rhythm — Monday priorities + scorecard, Friday review
    scheduler.add_job(
        run_monday_priorities,
        CronTrigger(day_of_week="mon", hour=8, minute=45, timezone=settings.scheduler_timezone),
        id="monday_priorities",
        name="Monday Weekly Cadence",
        replace_existing=True,
    )
    scheduler.add_job(
        run_friday_review,
        CronTrigger(day_of_week="fri", hour=15, minute=30, timezone=settings.scheduler_timezone),
        id="friday_review",
        name="Friday Weekly Review",
        replace_existing=True,
    )

    return scheduler


async def _run_now_flag(mode: str) -> None:
    """Developer shortcut: run a scheduled job immediately without waiting."""
    if mode == "brief":
        await run_morning_brief()
    elif mode == "eod":
        await run_eod_report()
    else:
        logger.error("Unknown --run-now mode: %s", mode)


async def main(run_now: str | None = None) -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.info(
        "ZYNTH Scheduler starting. Timezone: %s | Brief at %02d:%02d | EOD at %02d:00",
        settings.scheduler_timezone,
        settings.daily_brief_hour,
        settings.daily_brief_minute,
        settings.eod_report_hour,
    )

    if not settings.has_telegram:
        logger.warning(
            "Telegram not configured — scheduled reports won't be delivered. "
            "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
        )

    if run_now:
        await _run_now_flag(run_now)
        return

    scheduler = build_scheduler(settings)
    scheduler.start()
    logger.info("Scheduler running. Press Ctrl+C to stop.")

    try:
        await send_message(
            "⚡ <b>ZYNTH Scheduler started!</b>\n"
            f"📅 Morning brief: {settings.daily_brief_hour:02d}:{settings.daily_brief_minute:02d} Yangon time\n"
            f"🌙 EOD report: {settings.eod_report_hour:02d}:00 Yangon time\n"
            "Send /help to your bot for manual commands."
        )
        # Keep alive
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    run_now = None
    if "--run-now" in sys.argv:
        idx = sys.argv.index("--run-now")
        run_now = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "brief"

    asyncio.run(main(run_now=run_now))
