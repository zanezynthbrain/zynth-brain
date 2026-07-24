# ZYNTH — Session Handoff (read this first, one pass)

> Condensed digest regenerated at the end of every working session. The full
> chronological log is `CONTEXT.md`; the business bible is `docs/playbook/00`–`08`
> and `NORTH_STAR.md`. This file is the snapshot: where we are, what's open, what's next.

_Last updated: 2026-07-24 · Branch: `claude/zynth-multi-agent-framework-uk1a8i`_

## What ZYNTH is
AI-run marketing & events agency (Myanmar + Singapore). MD/sole approver: Zane
(zane@zynth.asia). 24/7 Telegram bot + scheduler on Railway (service
`fabulous-bravery`), Docker from repo root, auto-deploys on merge to `main`.
Repo `zanezynthbrain/zynth-brain` — **PUBLIC** (MD's decision; keys protected by
`.gitignore`, never committed). Flagship owned IP: IGNITE Summit, 14 Nov 2026.

## Current build status
- ✅ Core multi-agent backend, CEO daily cycle, proposal/event engines, venue +
  supplier + prospect DBs, market FX, knowledge base, dashboard, nightly consolidation.
- ✅ **BD Autopilot** (this session): research → Apollo contact enrichment →
  draft outreach → 1-tap/auto-release queue → send (SMTP), capped daily. Telegram:
  `/autopilot`, `/queue`, `/release`, `/reject`. Off until `BD_AUTOPILOT_ENABLED=true`.
- ✅ **Deep BD intelligence**: researcher outputs company_analysis, online/on-ground
  activities, marketing_gap, zynth_approach, target_role per prospect.
- ✅ Google Drive "Company OS" mirror (department folders + live BD Sheet).
- ✅ Security: `.gitignore` protects `.env`/keys (public repo).
- ⏳ Consultant "Master Build" Phases 1–7 in progress (this session).

## Consultant plan — phase status
1. Bridge — ✅ this file + `bridge/`.
2. Manus knowledge ingestion — ✅ all 8 Manus .docx ingested (market intel only):
   event calendar + sector spend/decision-makers + Top-20 event budgets (22),
   video crew/equipment rates (23), MM/SG media rates + competitors (24), campaign
   playbook + KPI/budget benchmarks (25), and the WavePay gold-standard proposal
   seeded into the best-of pool. Architecture recs (Haiku redesign, 5-agent video
   split, standalone campaign-planner) correctly NOT implemented.
3. Seven-block agent specs — ✅ `backend/agents/specs/` (event trio, proposal, BD, CMO).
4. Job file + Critic QC gate — ✅ `utils/jobfile.py` + `agents/critic.py`.
5. Proposal quality engine — ✅ "ZYNTH Proposal Standard" rename + rotating best-of.
6. BD data spine — ✅ (was ~80% built; full lead schema + `/bd enrich` + weekly export).
7. Cost audit + telemetry — ✅ tooling + `/cost` by agent/job; retro-scoring runs on demand.

## Open decisions waiting on MD
- **Anthropic API credit** — bot brain is offline/limited without it (top up in Console).
- **Provide the 8 Manus .docx** (Phase 2) so real MM market figures replace placeholders.
- **Merge working branch → main** to deploy this session's Phase 1–7 work.
- Rotate the GitHub token exposed in chat (optional; MD deferred).

## Known constraints / not-bugs
- Apollo free plan = 85 lead credits (enough for the A/B target list, not "thousands").
- Retro cost-audit scoring costs credit + needs the brain online — run `/costaudit` when ready.
- Railway disk is ephemeral → durable data lives in the repo (pool pattern).

## Exact next step
1. MD: add Anthropic credit + merge branch to `main`.
2. Verify live in Telegram: `/brief` → `/autopilot` → `/autopilot run` → `/queue`.
3. Then drop the Manus docs so Phase 2 figures go from placeholder → real.
