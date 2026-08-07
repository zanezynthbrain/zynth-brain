# ZYNTH — Running Decision Log (CONTEXT.md)

> Purpose: any Claude session (or human) reads this first and knows exactly
> where the project stands. Update every working session.
>
> **If the MD feels lost, point them to `NORTH_STAR.md` first.** The business
> bible is `docs/playbook/00`–`08` (agency model, pricing, KPIs, 90-day
> rollout). The tools serve that playbook; they are not the business.

## What ZYNTH is
Digital marketing & events agency (www.zynth.asia), Myanmar + Singapore.
Founder/MD: Zane (zane@zynth.asia). Goal: regional-level event agency run
by an AI multi-agent workforce with the MD as sole human approver (HITL).
Flagship: **IGNITE Myanmar Business Summit — 14 Nov 2026, Yangon** —
sponsorship-funded, ZYNTH-owned IP.

## Current system (live)
- **Runtime:** Telegram bot + APScheduler on Railway (service `fabulous-bravery`),
  Docker build from repo root `Dockerfile`, deploys on merge to `main`.
- **Repo:** github.com/zanezynthbrain/zynth-brain (PRIVATE). Backend in `backend/`.
  Working branch `claude/zynth-multi-agent-framework-uk1a8i` → PR → merge to main.
- **Agents:** CEO daily cycle (research → departments → synthesis), Proposal
  Factory (Haiku drafts → pool), MasterProposalAgent (full 8-section client
  docs → .docx via /proposal), BD/NOVA with approve buttons, creative pipeline.
- **Knowledge base:** `backend/knowledge/*.md` injected into every agent
  (services + R1-R5 financial law, SOPs, MM/SG vendor DBs, 21 playbooks).
- **Channels:** Telegram commands + free-text/voice chat (Gemini transcription,
  `gemini-flash-latest` with fallback list). Email via SMTP app password
  (proposals attached, learning brief) — configured when SMTP_PASSWORD set.
- **Proposal pool:** committed to repo by daily GitHub Actions workflow
  (07:00 SGT), survives redeploys.
- **FX:** `utils/fx.py` — MARKET rates (marketratedaily.com style), never CBM
  official. Live fetch best-effort → cache → `/fx set` manual. Injected into
  every agent prompt.

## Key decisions (chronological)
- **2026-07-12:** Railway chosen over laptop/GitHub-only (~US$5/mo accepted).
  Repo made private. Two Railway services → deleted duplicate, kept fabulous-bravery.
- **2026-07-12:** Cost discipline after ~$10 burn: drafts on Haiku
  (fallback model), Sonnet only for client-grade output; 240s LLM timeout
  (60s caused silent triple-billing); S$5/day cap, `/cost` visible.
- **2026-07-12:** Docs as deliverables: /proposal outputs .docx (8 sections,
  ZYNTH standard, 50% deposit clause). Drive = manual save from Telegram
  (no Drive API yet).
- **2026-07-13 (consultation):** Event-agency expansion approved with scope
  cuts: event team v1 = 3 agents (ConceptPlanner, Designer, Ops+Vendor);
  CampaignPlanner cut (CMO covers); Blender = text block only (no render
  automation); venue DB = repo JSON not SQLite (Railway FS is ephemeral);
  talent DB = Google Sheets via service account under zane@zynth.asia;
  enrichment = manual-paste + LLM formatting (no scraping).
- **MD answers on record:** no live leads yet (90-day focus = IGNITE + venue
  outreach + IGNITE-standard proposals); API budget ceiling S$40/month;
  NOTHING sends externally without MD confirmation (drafts only);
  all money figures use MARKET FX (sell side for client quotes).

## Build phases
1. ✅ CONTEXT.md + docs/event-knowledge + weekly MD Learning Brief (Mon 08:30 Yangon) + FX system + email channel
2. ✅ Venue DB — backend/data/venues.json (14 Yangon venues, all verified:false),
   /venue list|search|add|outreach; runtime adds → outputs/proposal_pool/venues_extra.json
   (committed daily by pool workflow); venue table injected into MasterProposal prompts;
   outreach emails are DRAFTS the MD forwards manually
3. ✅ Event team v1 — agents/event_team.py: ConceptPlanner + Designer +
   Ops/Vendor run in parallel on the cheap model, merge on primary model
   into 8-section docx; /event <brief> → document + Approve/Revise buttons;
   revise feedback flows into all specialists (max 3 cycles); approved docs
   emailed; Designer outputs a Blender MCP block (sent on approval, not in
   the client doc); per-cycle cost shown in the caption
4. ✅ Content & Design Studio — agents/content_studio.py: BrandStrategist
   (brand + owned-channel strategy, primary model) → ContentCreator (the
   month's calendar, EN + Myanmar captions) ∥ DesignDirector (visual system:
   palette/type/templates) → Designer (per-asset specs + render prompts).
   `/content <brand> <8|10|16|30>` → .docx + Approve/Revise (max 3 cycles).
   Packages in config/content_packages.py are CONTRACTUAL: volume, content-type
   mix, content:design ratio (6:8 · 7:10 · 11:16 · 19:30), videos, story sets,
   boosts, price band — the pipeline reconciles model output back onto them and
   reports every adjustment. Brand profiles + target audiences live in
   utils/brands.py (`/brandkit`), pool-persisted; unknown brands trigger
   open_questions, never invented facts. Artwork rendering via OpenAI
   (utils/imagegen.py) is MD-triggered by button and capped — specs and prompts
   ship with or without a key.
5. ✅ Meta publishing + Burmese-first craft + QC board (MD-approved 2026-08-04)
   - **Meta**: no connector exists, so `utils/meta.py` talks to the Graph API
     directly. Facebook posts are scheduled AT Meta (10 min–6 months, survives
     bot downtime); Instagram has NO scheduling API, so `scheduler.py` fires
     approved IG posts every 5 min (`publisher` switch, deliberately NOT
     master-gated — /quiet must never swallow an approved post). IG needs a
     public media URL → `utils/assets.py` serves `/assets/<token>/<file>` off
     the existing Railway public server (traversal-safe, extension-whitelisted).
   - **Approval gate**: `utils/publish_queue.py` — pending → approved →
     scheduled/published, pool-persisted. `/schedule <brand>` walks the month
     post by post with Approve/Skip; nothing reaches Meta unapproved. Dry-run
     (no token) shows exactly what WOULD be sent.
   - **Burmese**: `knowledge/26_myanmar_ad_craft.md` + MyanmarCopyChiefAgent.
     Content is now written Burmese-FIRST and transcreated to English; the Copy
     Chief owns the final Burmese, reports translation artifacts, and raises
     cultural flags (monks/pagodas/politics never campaign material).
   - **Motion**: MotionDesignerAgent — beat sheets, subtitle specs, CapCut/
     Premiere/Resolve edit specs, and OpenArt generation plans costed in credits
     BEFORE spending (PixVerse 50/5s volume → Seedance 400/5s hero).
   - **QC**: `utils/reviewboard.py` → `/review <brand>` renders a self-contained
     HTML board (artwork + MM/EN copy + specs + deterministic checks, Myanmar
     font embedded). `utils/compositor.py` composites brand-exact artwork from
     design specs with the vendored fonts — Burmese is ALWAYS typeset, never
     generated inside an image model.
6. ⬜ Talent DB (Google Sheets service account, /talent add manual-first)
- Not building yet: standalone CampaignPlanner agent (CMO covers it; the studio
  reads its output), Blender automation, scraping enrichment, hosted DB.

## Standing rules for any session working on this repo
- Never commit `.env` or real keys. `.env.example` placeholders only. (`.gitignore` enforces this — repo is PUBLIC.)
- Data that must survive redeploys lives in the repo (pool pattern), not the container.
- Agents may not quote UNVERIFIED numbers without the tag; verification is human work.
- Every external send (email/outreach) is draft-only → MD confirms (BD Autopilot uses a 1-tap/auto-release queue, capped daily).
- Nothing runs on a schedule unless its output has a NAMED CONSUMER (Phase 7 rule).
- Keep this file updated at the end of every session.
- **Session definition-of-done:** regenerate `HANDOFF.md`, run `python backend/tools/refresh_bridge.py`, commit, push.

## Command center + autonomy
- `utils/dashboard.py` renders a self-contained HTML command center (pipeline,
  proposals, suppliers, venues, scorecard, resources, system health) from live
  data. Served by a stdlib HTTP server in a daemon thread on $PORT (bot
  post_init) — Railway exposes it as a public URL (Settings → Networking).
  `/dashboard` also sends the HTML file to Telegram. `/health` route for probes.
- `scheduler.run_consolidation` (21:00 Yangon nightly): the bot reviews leads/
  suppliers on its own, computes deterministic gaps (stale leads, missing
  contacts, unverified), and the LLM turns them into a <250-word action digest
  to Telegram + email — "works like a department while the MD is away."

## Data collection layer (BD + sourcing, real records)
- `utils/suppliers.py` + `backend/data/suppliers_mm.json` — structured
  supplier/vendor DB across all categories (MC, DJ, Lighting, LED, Staging,
  Talent, Catering, Florist, Photo, Video, Printing, Fabrication) with
  company/tier/best_for/rate/lead_time/contact/phone/email/verified.
  `/vendor` list|search|add (AI structures free text). Runtime adds →
  outputs/proposal_pool/suppliers_extra.json (pool-persisted).
- `utils/leads.py` — client leads / BD pipeline; `/lead` add|list|stage,
  stages new→contacted→meeting→proposal→won/lost, open-value total.
  Persisted to outputs/proposal_pool/leads.json. NOTE: NOVA /bd could later
  auto-append qualified prospects here.
- Telegram truncation fixed: `_send_long` splits on paragraph/line
  boundaries (was hard-cutting at 4000 chars mid-word).

## Obsidian ↔ bot bridge
- Knowledge loader (utils/knowledge.py) now reads THREE sources: backend/
  knowledge/*.md (curated) + vault/**/*.md (Obsidian Git sync target, repo
  root, copied into the image) + outputs/proposal_pool/vault/**/*.md
  (instant /note captures, pool-persisted, live without redeploy).
- `/note <text or voice>` → cheap model titles/categorises → written to the
  live vault folder → agents use it immediately. Zero laptop setup.
- Bulk path: MD installs Obsidian Git plugin → syncs vault into repo-root
  `vault/` → reaches bot on next redeploy. Setup documented in vault/README.md.
- Dockerfile copies vault/ into the image; loader checks both local and
  /app layouts. Notes capped at 2.5k chars each; total budget 30k.

## Operating-system layer (bot carries the playbook rhythm)
- `utils/business.py` — Week 0 audit answers + 12-metric master scorecard,
  persisted to outputs/proposal_pool/business_state.json (survives redeploys).
- `/audit` — one-message (or voice) Week 0 Honest Audit → AI structures it →
  starting-line summary + top-3 priorities, emailed.
- `/scorecard` — view all 12 KPIs with 🟢🟡🔴 vs playbook targets/red-flags;
  `/scorecard set gross_margin 48` to update.
- Scheduler nudges: Monday 08:45 Yangon weekly cadence + scorecard snapshot;
  Friday 15:30 client-updates + weekly-review (the PROVE/EXPAND discipline).

## Proposal quality system
- 11-section IGNITE-standard schema, table-heavy (docgen renders real .docx tables).
- `backend/data/proposal_exemplar.md` = condensed IGNITE Master Proposal skeleton,
  injected as a few-shot GOLD-STANDARD reference into /proposal and /event merge prompts.
- Guided wizard: `/proposal` (no args) → buttons (type · market · scale) → one-line
  detail → assembled brief. `/proposal <text>` still works for power use.
- To raise the bar further, replace/extend proposal_exemplar.md with more approved
  examples (keep it a skeleton, ~8-10k chars, to control per-call cost).

## ZYNTH-OS integration + the learning loop (2026-08-07)
- **ZYNTH-OS Master Package integrated selectively.** Core docs → `docs/zynth-os/`
  (Operational Blueprint, Master Workflows, Industry Mapping, Tech Stack Map,
  SMM_1–8 references). **Adopted as skills** (flattened into `.claude/skills/`,
  each with a ZYNTH guardrail block appended — R1–R5, MM/SG, bilingual, HITL):
  `zynth-sponsorship-value`, `zynth-3d-production`, `zynth-tactical-prompts`.
  **34 skills now loadable.**
- **NOT adopted** (held readable in `docs/zynth-os/not-adopted/`, with reasons):
  `zynth-profit-planning` (YADANA owns finance — no second finance system),
  `zynth-creative-direction` + `zynth-agent-director` (collide with existing
  `zynth-creative-director` / `zynth-art-director` — near-identical descriptions
  make the wrong skill fire), `zynth-ads-management` (collides with
  `zynth-paid-media-specialist`), and the four video skills (2026-08-06 decision:
  video toolkit is a SEPARATE workspace for the volume tier).
- **Package defects found:** `tools/` and `templates/` shipped EMPTY though both
  docs promise Python automation and proposal templates; skills were nested by
  category so Claude Code could not load them (the guide's own `cp -R` command
  would have loaded nothing); no R1–R5 anywhere; `/home/ubuntu/` path shipped in
  the instructions. Blender *automation* claims conflict with the locked
  2026-07-13 decision (text block only) — adopted as spatial design knowledge.
- **NEW: the external learning loop** — `backend/utils/outcomes.py` + `/outcome`.
  The internal loop (mistakes → lessons → prompts, bestof exemplars) only ever
  graded its own homework. Now real results are recorded, judged against sourced
  external BENCHMARKS, and a metric that misses 3+ times (verified only) is
  promoted into `utils/lessons.py` — i.e. into every agent prompt. Unverified
  numbers never count toward a benchmark.
- **`docs/ZYNTH_MASTER_GUIDE.md`** — bilingual EN/Myanmar system map: storage
  (GitHub/Railway/Claude Code/Obsidian), the two-session git protocol, all 34
  skills, all commands, both learning loops, n8n comparison, interface options.

## Back-office cluster + video toolkit (2026-08-06, from the MD's other session)
> Full record: **`docs/handoff/2026-08-06.md`** — read it on session start
> (`CLAUDE.md` now points there).
- **Finding:** the open skill ecosystem is deep in dev/infra, thin in agency
  back-office. No HR skill and no agency-finance skill exist anywhere → both are
  build-from-scratch. Verdict lives in `docs/adoption/BACKOFFICE_ADOPTION_MANIFEST.md`.
- **`zb-` cluster built** (icp → offer → quote → objections → pitch-kit): one
  spine, one set of numbers, mapped to the 11-section Proposal Standard.
- **Finance controller agent, persona YADANA** (ရတနာ): quoting engine, project
  P&L, 13-week cashflow, invoicing SOP, xlsx model spec.
- **R1–R5 RECONCILED:** `backend/knowledge/01_zynth_services.md` is the single
  source of truth (35% floor, 50% deposit, 3-month runway, 80/20 mix, 20%
  reinvestment). The YADANA file's block gets replaced with it, not the reverse.
  ⚠️ The handoff's "block under 40% margin" contradicts R1 — correct behaviour is
  hard block <35%, amber 35–40%, green ≥40%. 40% is the target, 35% is the floor.
- **YADANA vs `utils/finance.py`:** brains vs ledger, not duplicates. YADANA
  decides whether a quote clears the floor; `finance.py` records what ZYNTH pays.
  YADANA reads `monthly_burn()` rather than restating it.
- **Video toolkit:** `digitalsamba/claude-code-video-toolkit` adopted as a
  SEPARATE workspace for the Factory/volume tier only — not merged, not the hero
  tier. Cherry-pick remotion/elevenlabs/ltx2/ffmpeg.
- **Trust map:** "VideoDraft MCP / rodneymbrown1/MCP-blender-video-editor" is
  HALLUCINATED — do not install. Real alternatives: KyaniteLabs/kinocut,
  chandler767/mcp-video-editor, burningion/video-editing-mcp. Do not fork the
  stack with CrewAI/AutoGen.
- **Framing:** MCP = hands (tool access), Skills = brains (domain knowledge).
- **LANDED 2026-08-06:** the pack was delivered and unpacked. `.claude/skills/`
  now holds the 5 new skills **plus all 21 previously user-level `zynth-*`
  department skills** — 31 skills total, all repo-versioned and travelling with
  every clone. `docs/adoption/` holds the manifest + pack README.
- **R1–R5 replaced in `yadana-finance` §3** with the canonical block, verbatim.
  §3.1 adds the green/amber/red banding (amber warns, only red blocks); §3.2 keeps
  the draft's four operational rules as "quoting discipline", deliberately NOT
  R-numbered so there is only ever one R-law. Fixed R-number drift inside the
  file: the deposit rule is **R2**, not R4.
- ⚠️ **Still open:** the xlsx workbook spec in the handoff still says "blocks any
  job under 40% margin". Build it to the BANDED model in `yadana-finance` §3.1,
  not to that line.

## Finance — operating costs (2026-08-05)
- **Money Out is live data:** `backend/utils/finance.py` + `backend/data/expenses.json`,
  readable via `/expenses`. Burn ≈ **US$60/month** (US$5 confirmed, US$55 estimated):
  Claude Pro, Anthropic API (ceiling S$40/mo), OpenArt Starter, zynth.asia domain,
  mobile+wifi US$5, Railway ~US$5. Unverified amounts carry `verified:false` and are
  reported with a TBC tag — never as fact. Budget sheet:
  `docs/departments/FINANCE_operating_costs.md`.
- **MD decision:** no production team yet → video is **edit-only, AI-generated**,
  building a portfolio at commercial level. Crew/equipment rates stay on file for
  client quotes (ZYNTH is producer-led), they are just not in the current burn.
- **AI credits are stock, not subscription.** Credits scale with SHOT COUNT, not
  runtime — every shot is a separate 5s-minimum generation. A 15s film at commercial
  pacing is ~8 shots: 972 (lean) / 2,524 (balanced) / 4,752 (premium) credits,
  including a ×1.35 retake factor. Recommended buy: **~8,700 credits** for
  3 × 15s balanced (one portfolio film per service line).
- OpenArt/openart.ai pricing is BLOCKED from the Railway/Claude environment, so the
  dollar cost of a credit pack is unverified — the MD reads it off the billing page.

## MD setup still pending
- Anthropic credit top-up (bot brain offline without it)
- OPENAI_API_KEY + ZYNTH_ALLOW_NETWORK=true in Railway → turns on artwork
  rendering in the design studio (specs and prompts work without it)
- META_ACCESS_TOKEN (System User token, Business Manager — never expires),
  META_PAGE_ID, META_IG_USER_ID → activates scheduling. Until then /schedule
  runs in dry-run and shows exactly what would be sent.
- ZYNTH_PUBLIC_URL + ZYNTH_ASSET_TOKEN → required for Instagram only (IG
  fetches media by URL; Facebook does not need it).
- OpenArt has 3,170 credits (Starter). Higgsfield is on 1 credit/free — not
  worth paying for while OpenArt covers image AND video. Canva has NO brand
  kit, so it can't enforce brand yet.
- Add real client brands via `/brandkit add` (brand + target audience) so the
  studio stops working from briefs alone
- SMTP_USER + SMTP_PASSWORD (Google App Password) in Railway → activates email
- Test Claude Desktop + Blender MCP on laptop (gates Designer's Blender block)
