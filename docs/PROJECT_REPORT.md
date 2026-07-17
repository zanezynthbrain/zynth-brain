# ZYNTH AI Agency — Full Project Report

*Generated 2026-07-17 · repo: `zanezynthbrain/zynth-brain` (private) · branch merged to `main`*

This is the complete record of what has been built: an AI-run operating
system for ZYNTH, a marketing & events agency serving Myanmar and Singapore.
Hand this file to any AI or teammate to bring them fully up to speed.

---

## 1. What ZYNTH is (and what this system does)

**ZYNTH** — "The Intelligence of Creativity." A dual-market (Yangon + Singapore)
marketing and events agency. Founder/MD: **Zane** (zane@zynth.asia).
Flagship owned IP: **IGNITE Myanmar Business Summit** — 14 Nov 2026, Yangon.

**The system** is a 24/7 AI workforce the MD operates from Telegram (and a web
dashboard). It generates proposals, runs a daily agency cycle, collects BD and
supplier data, tracks tasks, prices at real market rates, and reports —
so one founder + AI can operate like a much larger agency.

---

## 2. Architecture at a glance

| Layer | What it is |
|---|---|
| **Runtime** | Python async bot on **Railway** (service `fabulous-bravery`), 24/7, Docker build from repo root, auto-deploys on merge to `main`. |
| **Interface** | **Telegram bot** (28 commands + free-text/voice chat) and a **live web dashboard** on the same service. |
| **Brain** | Claude (Anthropic API). Cheap fallback model (Haiku) for high-volume drafts; primary model for client-grade output. |
| **Agents** | CEO daily cycle + department agents + specialist teams (below). |
| **Data** | JSON files in the repo (`backend/data/` + `outputs/proposal_pool/`), committed daily so they survive redeploys. |
| **Knowledge** | `backend/knowledge/*.md` + the Obsidian vault, injected into every agent prompt. |
| **Catch-up docs** | `CONTEXT.md` (decisions), `NORTH_STAR.md` (business↔system), `CLAUDE.md` (architecture), this report. |

---

## 3. The agent workforce (`backend/agents/`)

- **CEO** — runs the full day in waves: research → leadership (CMO/COO/CFO/HR/Events/Ops) → specialists (creative/BD/copy) → synthesis → Telegram report.
- **Proposal Factory** — high-volume idea drafts (industry × month × market) → the proposal pool.
- **Master Proposal** — the full **IGNITE-standard 11-section** client document (with real tables) → Word doc.
- **Event Specialist Team** — ConceptPlanner + Designer (+ Blender 3D block) + Ops/Vendor run in parallel → merged event proposal → HITL approve/revise (max 3 cycles).
- **NOVA / Lead Gen**, Copywriter, Research/SEO, Paid Ads, Portfolio, and the CMO/COO/CFO/HR/Operations/Event leadership agents.
- Every agent inherits ZYNTH brand voice + business knowledge + live market FX + the R1–R5 financial rules.

---

## 4. Every Telegram command (28)

**Command Center:** `/dashboard` (live interactive dashboard) · `/task` (add/list/done, by department) · `/status` (activation checklist)

**Databases:** `/lead` (BD pipeline: add/list/stage) · `/vendor` (supplier DB, all categories) · `/venue` (Yangon venues)

**Proposals & work:** `/proposal` (full IGNITE-standard Word doc + guided wizard) · `/generate` (quick idea drafts) · `/proposals` (pool stats) · `/event` (event team + HITL) · `/creative` · `/research` · `/ops` · `/bd` · `/pipeline` · `/brief` (full agency day) · `/report`

**Run the agency (playbook):** `/audit` (Week 0 Honest Audit) · `/scorecard` (12-metric master scorecard)

**Knowledge & config:** `/note` (quick capture → vault) · `/kb` (knowledge files) · `/fx` (market rates) · `/testemail` · `/cost` (spend vs budget) · `/approve` · `/run <workflow>` · `/help`

Plus **free text** and **voice messages** (Burmese/English) → the AI Chief of Staff.

---

## 5. Data & databases (real records, day by day)

- **Client leads / BD pipeline** — `leads.json`: company, contact, phone, email, industry, market, source, stage (new→contacted→meeting→proposal→won/lost), value, next step.
- **Supplier/vendor DB** — `suppliers_mm.json` (17 seed, all event categories): company, tier, best-for, rate, lead time, contact, verified.
- **Venue DB** — `venues.json` (14 Yangon venues): capacity by setup, location, floor-plan status, verified.
- **Tasks + activity feed** — `tasks.json` (department, status, assignee) and `activity.json` (rolling log of everything that happens).
- **Proposal pool** — accumulates generated proposals, committed to the repo daily.
- **Scorecard + audit** — `business_state.json`.
- **All figures carry a `verified` flag** — agents must tag unverified numbers "to be confirmed"; verification is human work.

---

## 6. What runs on its own (scheduler, Yangon time)

- **07:00** — market FX refresh · **08:00** morning CEO brief · **18:00** end-of-day report
- **07:00 SGT** — daily proposal batch (GitHub Actions, both markets, committed to repo)
- **21:00** — **nightly consolidation**: the bot reviews leads + suppliers, finds gaps (stale leads, missing contacts, unverified), and emails/messages an action digest
- **Mon 08:30** — MD Learning Brief (one event discipline + a regional trend) · **08:45** weekly cadence + scorecard · **Fri 15:30** client-update + weekly review

---

## 7. Infrastructure & channels

- **Deploy:** root `Dockerfile` builds `backend/`, runs `telegram_bot.py`; APScheduler starts in `post_init`; `tzdata` pinned for `Asia/Rangoon`.
- **Web dashboard:** stdlib HTTP server in a daemon thread on `$PORT`; `GET /api/state`, `POST /api/task`, `/health`. Railway can expose a public URL.
- **Voice:** Google Gemini transcription (free tier), MM + EN, model auto-fallback.
- **Email:** SMTP (Google App Password) — proposals, learning brief, consolidation.
- **Cost control:** hard daily S$ budget, `/cost` visibility, cheap model for drafts.

---

## 8. Business playbook, wired in

The MD's full agency playbook lives in `docs/playbook/00–09` (business model,
pricing, org/JDs, KPI system, operating rhythm, SOPs, back office,
differentiation, 90-day rollout, + a ZYNTH-reality addendum). Real service-line
pricing and the "speed moat" standards are in the agent knowledge base, so
proposals price on actual numbers. Event craft curriculum in `docs/event-knowledge/`.

---

## 9. Live now vs needs your setup

**Live (verified):** bot 24/7 · proposal engine (IGNITE-standard) · event team ·
databases · dashboard · market FX · voice · knowledge base · nightly automation.

**Needs one action from you:**
- Anthropic API credit (the brain is offline without it) — `/cost` to watch
- Railway → Settings → Networking → **Generate Domain** (permanent dashboard URL)
- Run **`/audit`** (2 hours) — sets the starting line, activates the scorecard
- Verify venue/supplier data via `/venue outreach` (call/email the venues)

---

## 10. Honest assessment

**What the system genuinely does well:** speed (48h proposal → 3 minutes), scale
(unlimited drafts), consistency, 24/7 availability, and structured data capture.

**What it cannot do — stays the MD's job:** deliver events on-site, qualify real
leads, verify vendor/venue numbers, close deals, and the PROVE/EXPAND client work
where agencies actually win. The tools are leverage; leverage on zero clients is
still zero. **The build is done; the business is the work now.**

---

## 11. How to review this with another AI

Everything is in the private repo `zanezynthbrain/zynth-brain`. To have any AI
(ChatGPT, Gemini, another Claude, Cursor, etc.) check it:

1. **Fastest:** GitHub → **Code → Download ZIP** → upload to the AI → ask it to
   "review this codebase; start with `CONTEXT.md`, `NORTH_STAR.md`, and
   `docs/PROJECT_REPORT.md`." Those three files are written to bring any reader
   up to speed instantly.
2. **Repo-connected AIs** (Claude Code, Cursor, Copilot): point them at the repo.
3. **Hand over this report** as the executive summary.
4. **Live data:** the dashboard's `GET /api/state` returns JSON of everything —
   any tool can read the current numbers from there.

Nothing is hidden or locked to one AI. The repo is the single source of truth,
and it is self-documenting by design.

---

## Appendix — feature history (merged PRs)

1. Multi-agent backend · 2. Railway Dockerfile build · 3. tzdata fix ·
4–5. Knowledge base + conversational bot + persistent pool · 6–8. Docs, daily
batch, ops-vault knowledge · 9–10. Timeout fix, Haiku drafts, Word docs ·
11–13. Voice (Gemini) · 14. Market FX + email + learning brief + CONTEXT ·
15. Venue DB · 16. Event Specialist Team + HITL · 17. Email-from · 18. IGNITE
11-section proposals · 19. Exemplar few-shot + wizard · 20. Playbook +
NORTH_STAR + pricing · 21. Operating system (/audit /scorecard /rhythm) ·
22. Obsidian bridge + /note · 23. Activation dashboard + reality addendum ·
24. Pool truncation fix · 25. /testemail · 26. Supplier + leads DB + truncation
fix · 27. Command center + nightly consolidation · 28. Interactive dashboard.
