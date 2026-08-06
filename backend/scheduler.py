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
import html
import sys
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

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

        # Refresh the Obsidian mirror, then push the whole day's output to GitHub
        # (one push/day → your Obsidian pulls it, and the data survives redeploys).
        try:
            from utils import obsidian, gitsync
            obsidian.full_sync()
            if gitsync.is_configured():
                ok, msg = await gitsync.sync("chore: nightly ZYNTH vault + data sync")
                logger.info("Git sync: %s", msg)
        except Exception as exc:
            logger.info("Git sync skipped: %s", type(exc).__name__)
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

        # Mirror the narrative into the Obsidian vault (best-effort).
        try:
            from utils import obsidian
            obsidian.research_log_entry(r["sector"], r["added"], r["total"], r["top"])
            obsidian.full_sync()
        except Exception as exc:
            logger.info("Obsidian mirror skipped: %s", type(exc).__name__)

        # Best-effort mirror to external databases (no-op until configured).
        await sync_prospects_out()
    except Exception as exc:
        logger.exception("Market research failed: %s", exc)


async def sync_prospects_out() -> None:
    """Push the prospect DB to Google Sheets + HubSpot if their credentials are
    set. Fully best-effort — a missing/failed sync never affects research."""
    try:
        from utils import sheets_sync
        if sheets_sync.is_configured():
            ok, msg = await asyncio.to_thread(sheets_sync.push_prospects)
            logger.info("Sheets sync: %s", msg)
    except Exception as exc:
        logger.info("Sheets sync skipped: %s", type(exc).__name__)
    try:
        from utils import hubspot_sync
        if hubspot_sync.is_configured():
            ok, msg = await hubspot_sync.push_prospects()
            logger.info("HubSpot sync: %s", msg)
    except Exception as exc:
        logger.info("HubSpot sync skipped: %s", type(exc).__name__)


async def run_weekly_bridge_export() -> None:
    """Monday: export the master lead + prospect databases to bridge/ (CSV) and
    refresh the build-state snapshot. Consumer: the MD's Drive/consultant."""
    import csv as _csv
    from pathlib import Path as _Path
    logger.info("📦 Weekly bridge export")
    try:
        bridge = _Path("../bridge") if _Path("../bridge").exists() else _Path("bridge")
        bridge.mkdir(parents=True, exist_ok=True)

        # Leads CSV
        try:
            from utils.leads import all_leads, LEAD_FIELDS
            rows = all_leads()
            with open(bridge / "leads.csv", "w", newline="", encoding="utf-8-sig") as f:
                w = _csv.DictWriter(f, fieldnames=["id"] + LEAD_FIELDS + ["created_at", "updated_at"], extrasaction="ignore")
                w.writeheader()
                for r in rows:
                    w.writerow(r)
        except Exception as exc:
            logger.info("leads export skipped: %s", type(exc).__name__)

        # Prospects CSV (reuse exporter)
        try:
            from utils.exporter import prospects_csv
            path, n = prospects_csv()
            import shutil as _sh
            _sh.copy2(path, bridge / "prospects.csv")
        except Exception as exc:
            logger.info("prospects export skipped: %s", type(exc).__name__)

        # Weekly cost report (Phase 7 telemetry) → bridge/
        try:
            from utils.costaudit import audit_text
            import re as _re
            plain = _re.sub(r"<[^>]+>", "", audit_text())
            (bridge / "cost_report.md").write_text(
                f"# ZYNTH Weekly Cost Report\n\n{plain}\n", encoding="utf-8")
        except Exception as exc:
            logger.info("cost report skipped: %s", type(exc).__name__)

        # Refresh HANDOFF/CONTEXT/knowledge snapshot
        try:
            import subprocess as _sp
            _sp.run(["python", "tools/refresh_bridge.py"], cwd=".", timeout=30, check=False)
        except Exception:
            pass

        await send_message("📦 <b>Weekly BD export → bridge/</b>\nleads.csv + prospects.csv refreshed for Drive / your consultant.")
    except Exception as exc:
        logger.exception("Weekly bridge export failed: %s", exc)


async def run_bd_autopilot() -> None:
    """The closed-loop BD engine: research → enrich real contacts (Apollo) →
    draft + queue personalised outreach → notify. Autonomous; you supervise.
    No-op unless BD_AUTOPILOT_ENABLED=true. Never raises out."""
    from utils import bd_autopilot
    if not bd_autopilot.is_enabled():
        return
    if bd_autopilot.is_paused():
        logger.info("BD autopilot paused — skipping")
        return
    logger.info("🤖 BD autopilot starting")
    try:
        from utils.prospects import recent
        r = await collect_prospects()  # research today's sector
        if r.get("mocked"):
            await send_message(
                "🤖 <b>BD Autopilot</b> is on but the brain is offline — add Anthropic "
                "API credit and it will research, enrich and queue outreach every day."
            )
            return
        # Enrich + queue the day's freshest, highest-fit prospects.
        new_rows = sorted(recent(days=1), key=lambda p: p.get("fit_score", 0), reverse=True)
        out = await bd_autopilot.enrich_and_queue(new_rows)
        await sync_prospects_out()

        apollo_note = "" if out["apollo"] else (
            "\n⚠️ Apollo not connected yet — set <code>APOLLO_API_KEY</code> in Railway so "
            "it can fill real contacts. Until then it drafts for prospects that already have an email."
        )
        await send_message(
            (
                f"🤖 <b>BD Autopilot — {r['sector']}</b>\n"
                f"Researched +{r['added']} · enriched {out['enriched']} real contacts · "
                f"drafted {out['queued']} outreach emails.\n\n"
                f"Review before they send: /queue{apollo_note}"
            )[:4000]
        )
        try:
            from utils.tasks import log_activity
            log_activity("BD", f"Autopilot enriched {out['enriched']}, queued {out['queued']} outreach", source="autopilot")
        except Exception:
            pass
    except Exception as exc:
        logger.exception("BD autopilot failed: %s", exc)


async def run_outreach_sender() -> None:
    """Send outreach that's due (released or auto-released), respecting the daily
    cap. Runs hourly. Honours the pause switch. No-op if nothing is due."""
    from utils import bd_autopilot, outreach
    if not bd_autopilot.is_enabled():
        return
    try:
        res = await outreach.send_due(paused=bd_autopilot.is_paused())
        if res.get("sent"):
            await send_message(
                f"📤 <b>Outreach sent:</b> {res['sent']} email(s) went out. "
                f"{res.get('skipped', 0)} still pending. /queue"
            )
            try:
                from utils.tasks import log_activity
                log_activity("BD", f"Autopilot sent {res['sent']} outreach emails", source="autopilot")
            except Exception:
                pass
    except Exception as exc:
        logger.info("Outreach sender error: %s", type(exc).__name__)


async def run_command_queue() -> None:
    """Drain commands the web Command Deck queued (every minute). Runs only the
    whitelisted actions and reports to Telegram. Browser buttons → real work."""
    try:
        from utils.cmdqueue import take_pending
        pending = take_pending()
    except Exception:
        return
    for cmd in pending:
        try:
            if cmd == "brief":
                await run_morning_brief()
            elif cmd == "research":
                await run_market_research()
            elif cmd == "autopilot":
                await run_bd_autopilot()
            elif cmd == "consolidation":
                await run_consolidation()
            elif cmd == "proposals":
                await run_daily_proposals()
            elif cmd == "costaudit":
                from utils.costaudit import audit_text
                await send_message(audit_text())
            elif cmd == "push":
                from utils import gitsync
                ok, msg = await gitsync.sync()
                await send_message(f"📤 <b>Sync:</b> {msg}")
            elif cmd == "improve":
                await run_self_improve()
        except Exception as exc:
            logger.info("queued cmd %s failed: %s", cmd, type(exc).__name__)
            try:
                from utils import mistakes
                mistakes.record("command", f"queued '{cmd}' failed", type(exc).__name__, "error")
            except Exception:
                pass


async def run_self_improve() -> None:
    """The self-improvement loop: ZYNTH reviews its own work, learns, and gets better.

    Reads the mistake log + metrics + activity, distils durable lessons, writes them
    into the injected knowledge file (so every agent improves), and reports the MD a
    short summary. Runs weekly + on demand (/improve, Command Deck)."""
    logger.info("🧠 Self-improvement review starting")
    try:
        from agents.improver import ImproverAgent, caption
        from utils import lessons
        llm = LLMClient()
        if llm.is_mocked:
            logger.info("Self-improve skipped — no API key")
            return
        review = await ImproverAgent(llm).review()
        added = lessons.add_many(review.get("lessons", []), source="weekly")
        try:
            from utils.tasks import log_activity
            log_activity("Operations", f"Self-review {review.get('health_score','?')}/10 · +{added} lessons", source="improve")
        except Exception:
            pass
        rec = review.get("recurring_mistakes", []) or []
        imp = review.get("improvements", []) or []
        msg = [
            f"🧠 <b>Self-Improvement Review</b> — health {review.get('health_score','?')}/10",
            f"<i>{review.get('self_assessment','')}</i>",
        ]
        if rec:
            msg.append("\n<b>Recurring mistakes:</b>\n" + "\n".join(f"• {html.escape(str(m))}" for m in rec[:3]))
        if imp:
            msg.append("\n<b>Improvements queued:</b>\n" + "\n".join(
                f"• {html.escape(str(i.get('action','')))}" for i in imp[:3] if isinstance(i, dict)))
        msg.append(f"\n📚 <b>+{added} new lesson(s)</b> written into every agent · {lessons.summary_line()}")
        await send_message("\n".join(msg))
    except Exception as exc:
        logger.exception("Self-improvement review failed: %s", exc)
        try:
            from utils import mistakes
            mistakes.record("self_improve", "review failed", type(exc).__name__, "error")
        except Exception:
            pass


async def run_daily_proposals() -> None:
    """Autonomous daily proposal production — the proposal department generates
    new event/campaign proposals every day, on its own, no prompting. Grows the
    library across industry × month × market, then mirrors to Obsidian."""
    logger.info("🏭 Daily proposal production starting")
    try:
        from agents.proposal_factory import ProposalFactoryAgent
        from utils.proposal_pool import ProposalPool

        llm = LLMClient()
        if llm.is_mocked:
            logger.info("Daily proposals skipped — no API key")
            return

        memory = SharedMemory(client_brief={"agency": "ZYNTH", "mode": "daily_proposals"})
        agent = ProposalFactoryAgent(llm)
        pool = ProposalPool()
        generated: list[str] = []
        for market in ("MM", "SG"):
            combo = agent.next_uncovered(market, pool)
            if combo is None:
                continue
            ind, mo = combo
            try:
                props = await agent.generate_batch(ind, mo, market, memory, pool)
                generated.append(f"{ind} × {mo} ({market}): {len(props)}")
            except Exception as exc:
                logger.warning("Proposal batch failed for %s × %s (%s): %s", ind, mo, market, exc)

        if generated:
            total = pool.get_stats().get("total", 0)
            await send_message(
                "🏭 <b>Proposal Factory — daily</b>\n"
                + "\n".join(f"• {g}" for g in generated)
                + f"\n\nLibrary now <b>{total}</b>. Browse: /proposals · Full doc: /proposal &lt;brief&gt;"
            )
            try:
                from utils import obsidian
                obsidian.full_sync()
            except Exception:
                pass
    except Exception as exc:
        logger.exception("Daily proposal production failed: %s", exc)


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



async def run_instagram_publisher() -> None:
    """Fire approved Instagram posts whose minute has arrived.

    Instagram has no scheduling API — Meta will not hold a post for us — so this
    IS the schedule for IG. It publishes only entries the MD already approved,
    which is why it checks its own switch with raw_on() instead of enabled():
    /quiet silences autonomous WORK, and must not silently swallow a post the MD
    already said yes to.
    """
    from utils import switches
    if not switches.raw_on("publisher"):
        logger.info("⏸  instagram publisher off")
        return
    from utils.publisher import run_due_instagram
    results = await run_due_instagram()
    for result in results:
        if not result.ok:
            await send_message(f"❌ Instagram publish failed: {html.escape(result.error[:300])}")
        elif result.action == "published":
            await send_message(f"🚀 Published to Instagram: {result.post_id}")


def _gated(job_key: str, fn):
    """Wrap a scheduled job so it only runs when its switch (and the master) is on.
    Manual runs (command queue / typed commands) call the underlying fn directly and
    are never gated — this only silences the AUTONOMOUS cron trigger to save API cost."""
    async def _wrapper():
        from utils import switches
        if not switches.enabled(job_key):
            logger.info("⏸  %s skipped (MD-only / switch off)", job_key)
            return
        await fn()
    _wrapper.__name__ = f"gated_{job_key}"
    return _wrapper


def build_scheduler(settings=None) -> AsyncIOScheduler:
    settings = settings or get_settings()
    scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)

    # Morning CEO brief
    scheduler.add_job(
        _gated("morning_brief", run_morning_brief),
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
        _gated("eod_report", run_eod_report),
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
        _gated("weekly_reviews", run_weekly_portfolio_review),
        CronTrigger(day_of_week="mon", hour=9, minute=0, timezone=settings.scheduler_timezone),
        id="weekly_portfolio_review",
        name="Weekly Portfolio Review",
        replace_existing=True,
    )

    # MD Learning Brief (Monday 08:30 Yangon = 10:00 SGT)
    scheduler.add_job(
        _gated("learning_brief", run_learning_brief),
        CronTrigger(day_of_week="mon", hour=8, minute=30, timezone=settings.scheduler_timezone),
        id="md_learning_brief",
        name="MD Learning Brief",
        replace_existing=True,
    )

    # Daily market FX refresh (07:00 Yangon, before the day's proposals)
    scheduler.add_job(
        _gated("fx_refresh", run_fx_refresh),
        CronTrigger(hour=7, minute=0, timezone=settings.scheduler_timezone),
        id="fx_refresh",
        name="Market FX Refresh",
        replace_existing=True,
    )

    # Autonomous daily proposal production (09:00 Yangon — grows the library)
    scheduler.add_job(
        _gated("daily_proposals", run_daily_proposals),
        CronTrigger(hour=9, minute=0, timezone=settings.scheduler_timezone),
        id="daily_proposals",
        name="Daily Proposal Production",
        replace_existing=True,
    )

    # Daily Myanmar market research (06:30 Yangon — new prospects before the day)
    scheduler.add_job(
        _gated("market_research", run_market_research),
        CronTrigger(hour=6, minute=30, timezone=settings.scheduler_timezone),
        id="market_research",
        name="Daily Market Research",
        replace_existing=True,
    )

    # BD Autopilot (07:00 Yangon — after research: enrich contacts + draft outreach)
    scheduler.add_job(
        _gated("bd_autopilot", run_bd_autopilot),
        CronTrigger(hour=7, minute=0, timezone=settings.scheduler_timezone),
        id="bd_autopilot",
        name="BD Autopilot",
        replace_existing=True,
    )
    # Outreach sender (hourly 09:00–18:00 Yangon — sends released/auto-released, capped)
    scheduler.add_job(
        _gated("outreach_sender", run_outreach_sender),
        CronTrigger(hour="9-18", minute=15, timezone=settings.scheduler_timezone),
        id="outreach_sender",
        name="Outreach Sender",
        replace_existing=True,
    )

    # Instagram publisher — every 5 minutes, because IG cannot be scheduled at
    # Meta. Facebook posts are already held by Meta and need nothing here.
    scheduler.add_job(
        run_instagram_publisher,
        IntervalTrigger(minutes=5, timezone=settings.scheduler_timezone),
        id="instagram_publisher",
        name="Instagram Publisher (approved posts)",
        replace_existing=True,
    )

    # Autonomous nightly consolidation (21:00 Yangon — while the MD is away)
    scheduler.add_job(
        _gated("nightly_consolidation", run_consolidation),
        CronTrigger(hour=21, minute=0, timezone=settings.scheduler_timezone),
        id="nightly_consolidation",
        name="Nightly Consolidation",
        replace_existing=True,
    )

    # Weekly operating rhythm — Monday priorities + scorecard, Friday review
    scheduler.add_job(
        _gated("weekly_reviews", run_monday_priorities),
        CronTrigger(day_of_week="mon", hour=8, minute=45, timezone=settings.scheduler_timezone),
        id="monday_priorities",
        name="Monday Weekly Cadence",
        replace_existing=True,
    )
    scheduler.add_job(
        _gated("weekly_reviews", run_friday_review),
        CronTrigger(day_of_week="fri", hour=15, minute=30, timezone=settings.scheduler_timezone),
        id="friday_review",
        name="Friday Weekly Review",
        replace_existing=True,
    )
    # Weekly BD export to bridge/ (Monday 08:00 Yangon — master lead DB to Drive)
    scheduler.add_job(
        _gated("weekly_reviews", run_weekly_bridge_export),
        CronTrigger(day_of_week="mon", hour=8, minute=0, timezone=settings.scheduler_timezone),
        id="weekly_bridge_export",
        name="Weekly BD Export → bridge/",
        replace_existing=True,
    )
    # Command-deck drain (every minute — web dashboard buttons → real work)
    scheduler.add_job(
        run_command_queue,
        CronTrigger(minute="*", timezone=settings.scheduler_timezone),
        id="command_queue",
        name="Command Deck Drain",
        replace_existing=True,
    )
    # Self-improvement loop (Sunday 20:00 Yangon — review the week, learn, get better)
    scheduler.add_job(
        _gated("self_improve", run_self_improve),
        CronTrigger(day_of_week="sun", hour=20, minute=0, timezone=settings.scheduler_timezone),
        id="self_improve",
        name="Self-Improvement Review",
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
