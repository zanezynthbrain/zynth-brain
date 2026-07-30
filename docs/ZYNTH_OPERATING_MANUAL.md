# ZYNTH Operating Manual — how to use everything we've built

**For: Zane (MD).** This is the one file that explains the whole system: what exists,
what each part is for, and exactly how to use it day to day. Read the "Start here"
section; use the rest as reference.

> Principle behind the whole system: **ZYNTH is AI-run. The agents DO the work; you
> decide.** You are *on* the loop, not *in* it. If you ever get a message that reads
> like a task for a team, that's a bug — tell me and I'll fix the agent.

---

## 0. Start here (the 5 things you actually touch)
1. **Telegram bot** — your control panel. Chat with it like a chief of staff, or use
   `/` commands. This is where you run and steer the agency. (See §2.)
2. **The Command Center dashboard** — the live HUD (vitals, pipeline, deliverables,
   command buttons) at your Railway URL. (See §3.)
3. **Claude Code (this project)** — where the deep work is produced. Ask for a
   campaign plan, event plan, proposal, video, HR doc, finance analysis — the skills
   (§4) turn it into a complete, costed deliverable.
4. **Google Drive — "ZYNTH Company OS"** — where every finished file lives, organised
   department by department, so you (and any future teammate) can find it. (See §5.)
5. **Obsidian** — the same knowledge, readable/editable on your laptop + iPad; syncs
   to the brain. (See §6.)

**Your daily rhythm (2 minutes):** open Telegram → read the morning brief → answer
any single decision it asks → glance at `/queue` (outreach waiting to send) →
release or reject. That's it. The agency runs the rest.

---

## 1. What's been built (the map)
| Layer | What it is | Where |
|---|---|---|
| **Multi-agent backend** | The AI departments (CEO, CMO, COO, CFO, HR, Events, Ops, Portfolio, BD, Creative) + orchestrator + QA gate | `backend/agents/` |
| **Telegram bot** | Your control panel, 24/7 | `backend/telegram_bot.py` |
| **Scheduler** | Autonomous daily/weekly jobs | `backend/scheduler.py` |
| **Skills** | Deep "how to do the work" engines (campaigns, events, video, BD, all specialists) | `.claude/skills/` |
| **Knowledge base** | ZYNTH's real facts the AI always uses | `backend/knowledge/` |
| **BD engine** | Continuous prospect research + Apollo enrichment + 1-tap outreach queue | `backend/utils/` (bd_autopilot, prospects, outreach, apollo_enrich) |
| **Command Center** | Live web dashboard | `backend/utils/dashboard.py` |
| **Department Operating Systems** | How each department actually runs (esp. HR + Finance) | `docs/departments/` |
| **Deploy** | Runs 24/7, auto-redeploys on merge to `main` | Railway + root `Dockerfile` |

---

## 2. The Telegram bot — your control panel
Talk to it in plain language ("what's our pipeline?", "draft a proposal for KBZ") or
use commands. The key ones:

**Run the agency**
- `/brief` — run the daily leadership brief now (agenda → departments → summary).
- `/audit` — the Week-0 Honest Audit: answer the questions once, it sets your
  "starting line". Redo anytime the business changes.
- `/proposals` — generate a fresh batch of proposals into the library.

**Business development (the money engine)**
- `/autopilot` — BD autopilot: `status` · `pause` · `resume` · `run`. When on, it
  researches prospects, enriches contacts (Apollo), and drafts outreach every morning.
- `/queue` — review outreach drafts waiting to send. `/release <id>` sends it,
  `/reject <id>` kills it. **This is your 1-tap send.** Nothing goes to a real
  prospect without you.
- `/enrich <company>` — build a full lead record (deep intel + Apollo contact) on demand.
- `/prospects` — the live prospect DB. `/export` → CSV for Sheets. `/sync` → push to
  Google Sheets / HubSpot.
- `/lead` — client leads & BD pipeline (`add` · `list` · `stage`).

**Money & accountability**
- `/costaudit` — spend last 7 days, cost per approved artifact, and the job audit
  (which scheduled jobs earn their keep). `/costaudit deep` re-scores past work.

**Knowledge & notes**
- `/note <text>` — capture a fact/idea; it's persisted and fed to every agent.
- `/kb` — list the active knowledge files the AI is using.

> Tip: if a reply is ever too long, just say "shorter" — the agents are told to lead
> with the answer and keep detail in the filed document.

---

## 3. The Command Center dashboard
Your live HUD at the Railway URL (`…up.railway.app`). Shows: system vitals, the BD
pipeline (6 stages), today's deliverables, spend vs cap, and command buttons that
enqueue the same actions as the bot (brief, research, autopilot, proposals, etc.).
Yangon clock. Use it when you want to *see* the state at a glance instead of scrolling
Telegram.

---

## 4. The Skills — where complete work gets produced
Skills are ZYNTH's deep expertise. In Claude Code (or when the bot routes to them),
just ask in plain language and the right skill activates. The heavy hitters:

- **`zynth-master-campaign-planner`** → a COMPLETE, costed marketing campaign plan
  (18 sections: strategy, creative direction, channels, ads, budget, suppliers,
  profit, sponsorship-vs-sell, ROI). All 18 sectors. Say *"full campaign plan for
  [client]"*.
- **`zynth-master-event-planner`** → a COMPLETE event plan (concept → run-of-show →
  suppliers → budget → funding model → ROI). Say *"event plan for [client]"*.
- **`zynth-creative-video-director`** → invent + craft video (concept, storyboard,
  Resolve/Premiere/CapCut craft, grading, VFX).
- The **specialist skills** (brand strategist, copywriter, paid-media, SEO, social,
  competitor/market research, account manager, vendor finder, BD researcher/pitch,
  pitch packager, project manager, analytics, art/creative director, event manager,
  campaign planner/requirements). These are the working roles of the agency.

**How to get a full deliverable:** name the client, the sector, the objective, the
budget band, and the market (MM/SG). Thin input = generic output; the skill will ask
2–3 sharp questions if you're vague.

---

## 5. Google Drive — the Company OS
Folder: **ZYNTH Company OS**, organised department by department (Marketing, Events,
BD/Sales, Creative, Finance, HR, Operations, Proposals, Knowledge). Finished files
live here with clear names so anything is findable.

- **What's mirrored:** proposals, plans, department operating systems, skills/docs,
  the BD lead sheet (a live Google Sheet), knowledge.
- **How it updates:** files I produce in a session are pushed here. Continuous
  day-by-day auto-update by the 24/7 bot needs a Drive service account wired into
  Railway — see §8 "What's not automatic yet".

---

## 6. Obsidian (laptop + iPad)
Your readable/editable knowledge vault. It syncs (Obsidian Git) to the same repo the
brain reads, so a note you write on the iPad reaches the agents on the next sync.
Use it to read SOPs, jot decisions, and keep the knowledge base current without
touching code.

---

## 7. The departments — who does what, and what reaches you
Each AI department produces real work and files it; only genuine owner-decisions
reach you. Full detail per department is in `docs/departments/`. The two you most
need (because you've said you have no experience there):
- **Finance** → `docs/departments/FINANCE_operating_system.md` — pricing, quoting,
  invoicing, payment terms, cash flow, monthly close, margins. Written so you can run
  it knowing only payroll.
- **HR** → `docs/departments/HR_operating_system.md` — hiring, contracts, onboarding,
  leave, payroll, performance, for MM + SG. Ready-to-use templates, not theory.
- Everything else (Marketing, Events, BD, Creative, Operations, Delivery) →
  `docs/departments/README.md`.

---

## 8. What's automatic vs what needs you
**Automatic (24/7):** morning brief, EOD report, nightly consolidation, daily
prospect research, BD autopilot enrich+draft, hourly outreach sending (MD-gated),
daily proposal batch, weekly review, FX refresh.

**Needs one tap from you:** releasing outreach to real prospects (`/queue`),
approving spend/hires, sending anything client-facing.

**Not automatic yet (honest list — I can build these next):**
- The 24/7 bot auto-writing to Google Drive every day (needs a Drive service account
  in Railway — right now Drive updates happen when I run a session).
- Real send of client emails end-to-end (drafting + queue is built; wiring the actual
  mail send is a switch to flip once you confirm the sending address).

---

## 9. If something looks wrong
- **A message reads like a task for a team** → it's a delegation bug; tell me the
  department and I'll fix its prompt.
- **An error in a channel** (e.g. "LLM call failed 400") → screenshot it; usually a
  model/credit/config issue, quick to fix.
- **You're getting too many messages** → tell me which channel; I'll cut the noise.

---

*This manual is itself mirrored to Drive (Knowledge folder). When we build something
new, it gets added here and to Drive so this stays the single source of truth.*
