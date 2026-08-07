<!-- TEMPLATE -->
<!-- Generated mirror — the knowledge loader skips this file on purpose. -->
---
generated: true
source: docs/handoff/2026-08-06.md
mirrored: 2026-08-07 09:42
---

> **Generated mirror of `docs/handoff/2026-08-06.md`.** Edit the source in the repo, not this
> file — the next `/mirror` overwrites whatever is here.

# CONTEXT — Session 2026-08-06 (Back-Office Build + Video Toolkit)

> Append this block to the repo's `CONTEXT.md` decision log (or keep as `docs/handoff/2026-08-06.md`
> and add one line to `CLAUDE.md`: "On session start, read docs/handoff/2026-08-06.md").
> This primes Claude Code with everything decided in the chat session of 2026-08-06.

## What was decided

**1. Moved to the back-office gap** (after the growth `zg-` cluster). Reviewed VoltAgent/awesome-agent-skills (~1000+), Corey Haines `marketingskills`, Kim Barrett `advertising-skills`.
- **Finding:** open ecosystem is deep in dev/infra, thin in agency back-office. **No HR skill and no agency-finance skill exist anywhere** → finance + HR must be built from scratch.
- Full verdict lives in `docs/adoption/BACKOFFICE_ADOPTION_MANIFEST.md` (adopt / adapt / build / skip).

**2. Built the `zb-` (ZYNTH back-office) cluster** — dual-purpose SKILL.md files (subagent + skill), model opus, ZYNTH guardrails (MM/SG, bilingual, HITL, R1–R5):
- `skills/zb-icp/` — define + score a prospect → feeds BD lead DB (adapts realkimbarrett/avatar-extraction)
- `skills/zb-offer/` — build a costed, compelling offer (adapts realkimbarrett/offer-extraction)
- `skills/zb-objections/` — pre-empt + neutralise objections (adapts realkimbarrett/objection-crusher)
- `skills/zb-pitch-kit/` — assemble the pitch package, mapped to the 11-section Proposal Standard (adapts coreyhaines31/sales-enablement)
- **Chain:** icp → offer → quote → objections → pitch-kit. One spine, one set of numbers.

**3. Built the Finance department + controller agent, persona YADANA** (Burmese ရတနာ "treasure/gems"; swappable):
- `skills/yadana-finance/SKILL.md` — quoting engine (bottom-up cost build → markup → margin check), working R1–R5 margin law, project P&L, 13-week cashflow/runway, invoicing/collections SOP, KPIs, and a §10 xlsx model spec.
- **ACTION for Claude Code:** the R1–R5 in this file is a clean working version. If a different R1–R5 already exists in the repo, **the existing one wins** — replace that block.

**4. Adopt-as-is engines** (install as baseline plugin, no adaptation): Anthropic `xlsx/docx/pptx/pdf/internal-comms/mcp-builder` + Google Workspace CLI (`gws-sheets/drive/gmail/calendar/docs`) + optionally Composio.

**5. Video toolkit decision:** adopt `digitalsamba/claude-code-video-toolkit` (MIT, ~1.8k stars) as a **separate cloned workspace** for the **Video Factory VOLUME tier** — NOT merged into zynth-brain, NOT the hero/cinematic tier. Cherry-pick its skills (remotion, elevenlabs, ltx2, ffmpeg) into zynth-brain. Ties to the existing two-tier model (factory = volume, ZED-crafted = hero).

**6. Trust-map correction** (a pasted list had errors): `ahujasid/blender-mcp`, `punkpeye/awesome-mcp-servers`, `OthmanAdi/planning-with-files` = real. **"VideoDraft MCP / rodneymbrown1/MCP-blender-video-editor" = HALLUCINATED — do not install.** Real video-edit MCP alts: `KyaniteLabs/kinocut`, `chandler767/mcp-video-editor`, `burningion/video-editing-mcp`. Do not fork the stack with CrewAI/AutoGen.

## Framing to carry forward
**MCP = hands (tool access). Skills = brains (domain knowledge).** The back-office gap was a brains gap — the `zb-` + YADANA files fill it. Pair with MCP tools for execution (e.g. QuickBooks MCP posts the invoice; YADANA decides if the margin clears the floor first).

## Pending (next actions)
- [ ] Build the live Finance `.xlsx` workbook to the §10 spec in `yadana-finance` (Quote Builder that blocks any job under 40% margin, Project P&L, 13-week cashflow, KPI dashboard).
- [ ] Reconcile R1–R5 (see action above).
- [ ] Commit the 5 new skill folders + `docs/adoption/BACKOFFICE_ADOPTION_MANIFEST.md` to the repo and push.
- [ ] Clone the video toolkit separately; report which skills to pull into zynth-brain.

## New files delivered this session (currently in Zane's Downloads, not yet committed)
```
skills/zb-icp/SKILL.md
skills/zb-offer/SKILL.md
skills/zb-objections/SKILL.md
skills/zb-pitch-kit/SKILL.md
skills/yadana-finance/SKILL.md
docs/adoption/BACKOFFICE_ADOPTION_MANIFEST.md
README.md   (integration guide + trust-map)
```

---

## ADDENDUM — reconciled against the repo (post Claude Code review)

Claude Code inspected `zynth-brain` and surfaced two conflicts. **Both are already fixed in the files in this pack** — no further reconciliation needed on these points:

**1. The finance ledger already exists.** `utils/finance.py` + `data/expenses.json` (live Money Out register, `/expenses`) and `docs/departments/FINANCE_operating_costs.md` (burn ≈ US$60/mo) were built prior to this session. `yadana-finance` §6.1 now states the division of labour explicitly — **YADANA is brains, `finance.py` is the ledger** — and requires YADANA to call `monthly_burn()` rather than restate burn figures. Overhead % (§2 Step 3) should be derived from the ledger once history allows, not left at the 15% default. Do not build a second finance system.

**2. Margin model is banded, not a flat floor.** The repo uses green ≥40% / amber 35–39.9% ("below target, above floor, justify it") / red below floor. This supersedes the flat "block below 40%" in the working draft. `yadana-finance` §3 and §10 now instruct the banded implementation: amber warns and requires written justification; only red blocks.

**3. Skill placement (action for Claude Code):** put the `zb-` cluster and `yadana-finance` in **`.claude/skills/`** (repo-versioned, travels with every clone) — NOT `~/.claude/skills/`. Also move the existing user-level department skills (`zynth-art-director` and the rest of the `zynth-*` set) into `.claude/skills/` at the same time, so a fresh session or another machine has them.

**4. Delivery:** the five skill files + manifest + README are delivered as `zynth-backoffice-pack.zip`. Unzip into the repo; they did not previously exist there.

---

# Appendix — repo reconciliation (Claude Code)


## R1–R5 — RESOLVED: the repo's version wins

The canonical block already exists at
**`backend/knowledge/01_zynth_services.md` → "Financial governance (R1–R5 —
these are LAW in every proposal/pitch)"**, and it is injected into *every* agent
prompt through `utils/knowledge.py`. It reads:

| | Rule |
|---|---|
| **R1** | Minimum **35% gross margin** on any quote — below this gates for MD approval |
| **R2** | Every proposal states a **50% deposit before work starts** — no exceptions |
| **R3** | Maintain **≥ 3 months cash runway** — Ops flags when below |
| **R4** | Revenue mix target **80% retainer / 20% project**; flag when project revenue exceeds 40% |
| **R5** | **20% of profit** reinvested into the AI stack |

**Replace the R1–R5 block in `yadana-finance/SKILL.md` with the above verbatim**
when that file is committed. Do not edit `01_zynth_services.md` to match the
skill — the knowledge base is the single source of truth and the agents read it.

### ⚠️ Conflict to fix in the workbook spec
The handoff specifies a Quote Builder that **"blocks any job under 40% margin."**
That contradicts R1. In this repo, **40% is the target, 35% is the floor**
(see `agents/specs/event_designer.md`: "35% floor / 40% target / 50% deposit /
10% contingency"). Correct behaviour for the workbook:

- **< 35%** → hard block. Requires MD dual approval to proceed (R1 + approval gate).
- **35–39.9%** → amber warning: "below target, above floor — justify it."
- **≥ 40%** → green.

A hard block at 40% would refuse work that R1 explicitly permits.

## What already exists here (do not rebuild)

| Handoff item | Already in repo | Note |
|---|---|---|
| Finance department | `docs/departments/FINANCE_operating_system.md` | The operating doctrine — pricing, payment terms, monthly close |
| Money Out / burn | `backend/utils/finance.py` + `backend/data/expenses.json` | Live cost register, `/expenses`, `/expenses burn` |
| Operating cost budget | `docs/departments/FINANCE_operating_costs.md` | Burn ≈ US$60/mo, AI credit planning per film |
| API spend tracking | `backend/utils/cost_tracker.py`, `costaudit.py` | Daily cap, `/cost`, `/costaudit` |
| Proposal standard | `backend/data/proposal_exemplar.md` | The 11 sections `zb-pitch-kit` must map to |
| Lead DB (for `zb-icp`) | `backend/utils/leads.py`, `prospects.py` | `/lead`, `/prospects` — icp scores should write here |

**YADANA and `utils/finance.py` are complementary, not duplicates** — and the
handoff's own framing explains why. YADANA is *brains*: does this quote clear the
floor, what is the P&L, what is the 13-week position. `finance.py` is the
*ledger*: what ZYNTH actually pays to stay switched on. YADANA should read
`monthly_burn()` rather than restate those numbers.

## Skill placement convention

Repo-versioned skills live in **`.claude/skills/<name>/SKILL.md`** (as
`zynth-creative-video-director`, `zynth-master-campaign-planner` etc. do).
User-level skills in `~/.claude/skills/` are NOT versioned and do not travel
with the repo. **Put the `zb-` cluster and `yadana-finance` in
`.claude/skills/`** so every session and every clone gets them.

## Landed 2026-08-06 (was blocked)

The pack was delivered and unpacked. Now in the repo:
- `.claude/skills/{zb-icp,zb-offer,zb-objections,zb-pitch-kit,yadana-finance}/SKILL.md`
- `docs/adoption/BACKOFFICE_ADOPTION_MANIFEST.md` + `BACKOFFICE_PACK_README.md`
- All 21 previously user-level `zynth-*` department skills, now repo-versioned

Applied on the way in:
1. `yadana-finance` §3 — the working-draft R1–R5 replaced with the canonical
   block from `backend/knowledge/01_zynth_services.md`, verbatim, as the file
   itself instructed.
2. §3.1 added — the green/amber/red banding, so amber warns and only red blocks.
3. §3.2 added — the draft's four operational rules kept as "quoting discipline",
   deliberately NOT numbered R1–R5 so there is only ever one R-law.
4. §6.1 ledger paths corrected to `backend/utils/finance.py` and
   `backend/data/expenses.json`.
