<!-- TEMPLATE -->
<!-- Generated mirror — the knowledge loader skips this file on purpose. -->
---
generated: true
source: docs/adoption/BACKOFFICE_ADOPTION_MANIFEST.md
mirrored: 2026-08-07 05:48
---

> **Generated mirror of `docs/adoption/BACKOFFICE_ADOPTION_MANIFEST.md`.** Edit the source in the repo, not this
> file — the next `/mirror` overwrites whatever is here.

# ZYNTH — Back-Office Adoption Manifest

**Scope:** BD, Sales, Finance, HR, Automation
**Sources reviewed:** VoltAgent/awesome-agent-skills (~1,000+), coreyhaines31/marketingskills (32), realkimbarrett/advertising-skills (12)
**Method:** same call as the growth cluster — ADOPT as-is / ADAPT with ZYNTH guardrails / BUILD our own / SKIP.

---

## The honest finding

The open ecosystem is **deep in developer/infra, thin in agency back-office.** ~90% of the VoltAgent list is test frameworks, Azure/AWS SDKs, database and deploy tooling — not for us. Critically:

- **No HR skill exists** in either catalog. HR = build our own.
- **No agency-finance skill exists.** "Stripe" skills are payment-*integration code*; "pricing-strategy" is SaaS-literal. Finance = build our own, on the xlsx engine.
- The genuine external wins are: **Anthropic's own doc/data/build skills** as engines, **Google Workspace CLI skills** (because our Company OS lives on Google), a **small BD/sales layer** from Corey Haines + Kim Barrett, and **automation plumbing** (Composio, mcp-builder).

---

## ADOPT as-is — install, don't touch

These are engines and access layers. Install as a plugin/baseline; no adaptation needed.

**Production + build engines (Anthropic official)**
- `anthropics/xlsx` — the actual engine for every financial model, quote, P&L, dashboard
- `anthropics/docx` — JDs, contracts, SOPs, HR docs
- `anthropics/pptx` — pitch decks, board decks
- `anthropics/pdf` — proposal export, form filling
- `anthropics/internal-comms` — status reports, newsletters, FAQs (HR + ops)
- `anthropics/mcp-builder` — wrap HubSpot / proposal pool / vault as your own MCP servers
- `anthropics/skill-creator` — you already use this pattern; keep it standard

**Google Workspace CLI (`gws`) — high value, because your OS is on Google Drive/Sheets**
- `googleworkspace/gws-sheets` — read/write the BD lead DB + finance sheets programmatically
- `googleworkspace/gws-drive` — Company OS folder automation (00–13)
- `googleworkspace/gws-gmail` — outreach + notify (replaces part of the Make.com Gmail step)
- `googleworkspace/gws-calendar` — event + ops scheduling
- `googleworkspace/gws-docs` / `gws-slides` — auto-produce handbooks and decks
- `googleworkspace/gws-tasks` — ops task tracking
- *(Requires the `gws` CLI + Workspace auth once; then agents drive it.)*

**Automation layer (optional but strong)**
- `composiohq/composio` — connect agents to 1000+ apps with managed auth; complements n8n for the app-integration jobs n8n makes clumsy

---

## ADAPT — vendor + wrap with ZYNTH guardrails (the `zg-` pattern)

Thin ZYNTH layer over each: MM/SG reality, brand voice, bilingual, HITL + R1–R5 gates. Suggested new prefix: **`zb-`** (ZYNTH back-office).

**BD / Sales**
- `coreyhaines31/sales-enablement` → **zb-pitch-kit** — pitch decks, one-pagers, objection-handling docs, demo scripts, mapped onto your 11-section Proposal Standard
- `realkimbarrett/offer-extraction` → **zb-offer** — turn a service into a high-converting offer (feeds proposals + BD)
- `realkimbarrett/objection-crusher` → **zb-objections** — pre-empt and neutralise client hesitation (BD + sales calls)
- `realkimbarrett/avatar-extraction` → **zb-icp** — sharpen prospect/ICP definition before outreach (feeds your BD lead DB)
- `realkimbarrett/performance-diagnosis` → fold into your existing **paid-media** skill, don't stand up separately (dedupe)

**Finance (reference only, not a full adopt)**
- `coreyhaines31/pricing-strategy` → mine for packaging/anchoring logic only; your productized tiers + R1–R5 margin law already own the substance

> Kim Barrett's `headline-matrix`, `mechanism-builder`, `ad-angle-multiplier`, `scroll-stopping-creative`, `conversion-path-builder`, `generic-language-killer` overlap your existing creative/copy squad (SAGAR, ZED, paid-media). Keep ZYNTH primary; cherry-pick tactics into those, don't install as rivals.

---

## BUILD our own — nothing worth adopting exists

**Finance department** (build on `xlsx` + `docx`)
- Agency financial model, per-project P&L, quoting engine, cashflow, margin guardrails (R1–R5 already drafted), retainer economics, MM/SG tax + FX reality. No repo covers agency finance — this is fully yours.

**HR department** (build on `docx` + `internal-comms`)
- JDs, KPI frameworks, hiring + onboarding SOPs, contractor/freelancer management, performance review cadence. Zero HR skills in either catalog — fully yours. You've already started this in the operating-model build; formalise it to ZED-depth.

**Moat (unchanged):** event ops, stage/exhibition/booth 3D, MM/SG market, brand, video craft.

---

## SKIP — huge but irrelevant (ignore the noise)

Do not spend attention here. This is ~90% of the VoltAgent list:
- All TestMu/LambdaTest test frameworks (~48)
- All Microsoft Azure SDK skills (133)
- Sentry SDKs, HashiCorp/Terraform, Cloudflare/Netlify/Vercel/Neon/Supabase/ClickHouse infra
- WordPress, Apollo GraphQL, Better Auth, Binance/Coinbase crypto, DuckDB, Redis, NVIDIA, Flutter/Expo/Angular/React-Native

---

## BONUS — AI-generated video + 3D (you asked separately)

These are **skill-wrapped access to generation models** — the closest thing to installable "commercial AI video/3D agents." They complement Higgsfield + OpenArt (which you already have connected), they don't replace your craft squad.

- `fal-ai-community/fal-3d` — text/image → 3D models (fast concept geometry to feed Blender/VERA)
- `fal-ai-community/fal-kling-o3` — Kling's top model family for video
- `fal-ai-community/fal-generate` — image + video generation
- `fal-ai-community/fal-video-edit` — restyle / upscale / bg-remove / add audio on existing video
- `fal-ai-community/fal-lip-sync` — talking-head + dub sync (pairs with your ElevenLabs VO step)
- `fal-ai-community/fal-upscale` — finish-grade upscaling
- `replicate/replicate` — one skill, hundreds of models, compare + run
- `remotion-dev/remotion` — programmatic video via React (your gold-black template factory could render here)
- `openai/sora` — Sora clips via API

**Verdict:** commercial quality comes from tool choice + your craft agents (ZED / YAZAWIN / PANCHI / AKYO / YEIN / VERA), not from a downloadable skill. These just widen the model shelf your Video Factory can call.

---

## Recommended sequence

1. Install the **ADOPT** engines + `gws` skills as a baseline plugin — instant back-office leverage, zero build.
2. Vendor the **4 `zb-` BD/sales adaptations** the same week you next touch a proposal.
3. Block time to **BUILD finance + HR** to ZED-depth — these have no shortcut.
4. Add the **fal.ai / Replicate** skills to the Video Factory shelf when you next iterate it.
5. Keep everything in `zynth-brain`. One source of truth.
