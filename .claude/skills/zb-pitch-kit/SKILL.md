---
name: zb-pitch-kit
description: ZYNTH back-office sales skill. Use to assemble the sales collateral around a proposal — pitch deck, one-pager, objection pre-empt, demo/walkthrough script — mapped onto the 11-section ZYNTH Proposal Standard. Adaptation layer over coreyhaines31/sales-enablement. Trigger for "build the pitch kit", "one-pager for this client", "sales deck", "demo script", "prep the pitch".
model: opus
sources: [chat]
adapts: coreyhaines31/sales-enablement
---

# zb-pitch-kit — ZYNTH Sales Enablement

**Upstream:** `coreyhaines31/sales-enablement` (pitch decks, one-pagers, objection docs, demo scripts).
**What ZYNTH adds:** everything maps onto the **11-section ZYNTH Proposal Standard** and the brand system (gold/black, "Intelligence of Creativity"), pulls its inputs from `zb-icp` / `zb-offer` / `zb-objections`, and its numbers from the Finance quoting engine (`YADANA`). This skill *assembles*; it does not re-derive.

## What the kit contains
1. **Pitch deck** — the proposal in presentation form, following the 11-section standard.
2. **One-pager** — the offer sheet compressed to a single leave-behind (outcome → mechanism → tiers → move-now).
3. **Objection pre-empt** — the "You might be wondering…" block from `zb-objections`.
4. **Demo / walkthrough script** — how Zane talks through the deck live, section by section, with the transitions and the ask.

## Mapping to the 11-section Proposal Standard
Each kit piece is built from the same spine so nothing contradicts:
1. Cover / brand frame → deck cover, one-pager header
2. Client challenge (from `zb-icp`) → deck slide 2, one-pager top line
3. ZYNTH understanding / insight → the mechanism
4. Strategic approach → deck core
5. Scope & deliverables (tiered) → one-pager tier table
6. Creative direction → deck visuals (brand system)
7. Timeline → deck + one-pager
8. Investment (from `YADANA` quote) → deck price slide, anchored per `zb-offer`
9. Why ZYNTH → mechanism + edge
10. Objection pre-empt → the "wondering" block
11. Next step / the ask → demo script close

## Build sequence
`zb-icp` (who + fears) → `zb-offer` (the offer) → `YADANA` (the price) → `zb-objections` (pre-empts) → **`zb-pitch-kit` assembles** → deck via `pptx`, one-pager via `docx`/`canvas-design`, export via `pdf`.

## Output
A complete, brand-consistent pitch package: deck (.pptx), one-pager (.pdf), objection sheet, demo script. Bilingual where the account requires it.

## Guardrails
- Never contradict the offer, the quote, or the tier language across pieces — one spine, one set of numbers.
- Brand system enforced (read `zynth-brand-identity` before any visual).
- Creative guardrail: no religious/sacred imagery.
- HITL: full package approved by Zane before it goes out.
