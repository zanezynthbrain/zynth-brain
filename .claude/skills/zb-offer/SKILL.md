---
name: zb-offer
description: ZYNTH back-office BD skill. Use to turn a ZYNTH service into a high-converting, costed offer — core deliverable, bonuses, risk-reversal, price anchor — mapped to our productized tiers and margin law. Adaptation layer over realkimbarrett/offer-extraction. Trigger for "build an offer", "package this service", "how do we present the price", "make this compelling", "offer for this client".
model: opus
sources: [chat]
adapts: realkimbarrett/offer-extraction
---

# zb-offer — ZYNTH Offer Construction

**Upstream:** `realkimbarrett/offer-extraction` (product → irresistible offer).
**What ZYNTH adds:** our productized service tiers (video T1–T5, event management), the R1–R5 margin law as a hard floor, MM/SG price reality in the right currency, and output that drops straight into the proposal (`zb-pitch-kit`) and the quote (Finance / `YADANA`).

## The ZYNTH offer stack
Build every offer in this order, and never lead with price:

1. **Core outcome** — the business result the buyer named in `zb-icp`, restated as the promise. (Not "6 reels" → "a launch month that fills the room and gets shared.")
2. **The mechanism** — *why ZYNTH's way works and the last agency's didn't.* This is our differentiation: bilingual MM/SG, event + video under one roof, intelligence-led creative. One sentence, specific.
3. **Deliverable stack** — what they actually receive, itemised, tied to a service tier so it's costable.
4. **Value amplifiers** — bonuses that cost us little and signal a lot (e.g. a post-campaign performance readout, a reusable brand asset, priority slot). Never discount the core; add to it.
5. **Risk reversal** — a milestone/gated structure or a clear revision policy, not money-back. Reduces the "new agency" fear surfaced in `zb-objections`.
6. **Price anchor + framing** — present the mid tier against a higher tier so the recommendation looks like the sensible choice. Anchor high, recommend middle.
7. **Reason to move now** — the real trigger (launch date, fiscal window, slot availability) — never fake scarcity.

## Costing law (non-negotiable)
Every offer is checked against **R1–R5 margin law** before it leaves. The price is built by the Finance quoting engine (`YADANA`), not guessed here — this skill defines *what's in the offer*; Finance sets *what it costs*. If the compelling version breaks margin, change the deliverable stack, not the floor.

## Currency + market
- SG accounts: SGD, GST-aware phrasing (not tax advice — flag to review).
- MM accounts: price in the currency the client contracts in; state FX assumption if cross-border.
- Tier language stays consistent with the public productized tiers so we never contradict our own rate card.

## Output
A one-page **Offer Sheet**: outcome → mechanism → stack → amplifiers → risk reversal → anchored price → move-now reason. Bilingual where the account operates bilingually. Hands to `zb-pitch-kit` for the full proposal and to `YADANA` for the costed quote.

## Guardrails
- Margin floor (R1–R5) always wins over persuasion.
- No fake urgency or invented scarcity.
- Creative guardrail carries through: no religious/sacred imagery in any concept referenced.
- HITL: offer + quote approved by Zane before it reaches the client.
