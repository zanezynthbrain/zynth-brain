# ZYNTH — Running Decision Log (CONTEXT.md)

> Purpose: any Claude session (or human) reads this first and knows exactly
> where the project stands. Update every working session.

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
4. ⬜ Talent DB (Google Sheets service account, /talent add manual-first)
- Not building yet: CampaignPlanner, Blender automation, scraping enrichment, HubSpot, hosted DB.

## Standing rules for any session working on this repo
- Never commit `.env` or real keys. `.env.example` placeholders only.
- Data that must survive redeploys lives in the repo (pool pattern), not the container.
- Agents may not quote UNVERIFIED numbers without the tag; verification is human work.
- Every external send (email/outreach) is draft-only → MD confirms.
- Keep this file updated at the end of every session.

## MD setup still pending
- Anthropic credit top-up (bot brain offline without it)
- SMTP_USER + SMTP_PASSWORD (Google App Password) in Railway → activates email
- Test Claude Desktop + Blender MCP on laptop (gates Designer's Blender block)
