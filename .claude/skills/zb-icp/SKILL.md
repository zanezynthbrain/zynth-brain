---
name: zb-icp
description: ZYNTH back-office BD skill. Use to define and score a prospect or ICP before outreach — who the buyer is, what they want, what they've tried, what's driving the decision — and to populate the BD lead DB. Adaptation layer over realkimbarrett/avatar-extraction. Trigger for "define our ICP", "who is this buyer", "profile this prospect", "should we pitch them", "score this lead".
model: opus
sources: [chat]
adapts: realkimbarrett/avatar-extraction
---

# zb-icp — ZYNTH ICP & Prospect Definition

**Upstream:** `realkimbarrett/avatar-extraction` (buyer definition for direct-response).
**What ZYNTH adds:** MM/SG B2B reality (this is a marketing/events agency selling to brands, not a DTC funnel), a fit-score that routes into the BD pipeline, bilingual output, and the exact fields our BD lead DB needs. Sits upstream of `zynth-bd-researcher` (which does the web recon) and feeds `zb-offer` + `zb-pitch-kit`.

## When this runs
Before any outreach, and whenever a new sector or named account enters the pipeline. Output is one **ICP Card** per target (a segment) or **Prospect Card** per named account.

## The ZYNTH buyer frame
For each target, extract and state plainly (EN + MM):

1. **Who signs / who champions** — the real decision-maker vs the influencer. In MM/SG SME brands this is often the MD/owner; in MNCs it's a Marketing/Brand Manager with a procurement gate. Name both roles.
2. **What they want** — the business outcome, not the deliverable ("more qualified walk-ins for the launch", not "a video").
3. **What they've tried** — previous agencies, in-house attempts, freelancers — and why it disappointed. This is the wedge.
4. **What's driving the decision now** — the trigger event (launch, rebrand, new fiscal budget, competitor move, expansion into MM or SG).
5. **Budget signal** — are they already spending (ads running, events done, sponsorships)? Visible spend > stated intent.
6. **Fear / risk they carry** — wasted budget, looking bad to their boss, launch slipping. Objections live here (hand to `zb-objections`).

## Fit score (routes the pipeline)
Score 0–3 on each; sum → band:
- **Budget capacity** (can they pay ZYNTH tier pricing?)
- **Need intensity** (is the trigger live or hypothetical?)
- **Decision access** (can we reach the signer?)
- **ZYNTH edge** (do events / video / MM-SG bilingual give us an unfair advantage here?)

Bands: **Hot 10–12 → outreach now** · **Warm 6–9 → nurture + research** · **Cold 0–5 → park.** Mirror the Hot/Warm/Cold bands already used in `zynth-bd-researcher` so scores are consistent across the funnel.

## Required output → BD lead DB fields
Every Prospect Card must fill these (they are the lead DB schema):
`brand · website · FB / TikTok / Meta pages · ads currently running (Y/N + platforms) · on-ground activity seen · sector · fit band` — plus, per contact: `name · position · LinkedIn · email · phone`. Leave blanks explicit ("phone: unknown — find") so the researcher knows what to chase.

## Guardrails
- Fit score is evidence-based; visible spend and trigger events outrank vibes.
- Do not invent contact details — mark unknowns.
- HITL: Hot cards go to Zane before outreach fires.
- Bilingual: buyer psychology in the language the account actually operates in.
