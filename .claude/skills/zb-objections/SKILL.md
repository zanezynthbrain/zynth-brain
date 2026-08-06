---
name: zb-objections
description: ZYNTH back-office BD skill. Use to pre-empt and neutralise client hesitation — price, in-house doubt, trust in a new agency, ROI doubt, timing, "let me think about it" — with reframes and response scripts in EN + MM. Adaptation layer over realkimbarrett/objection-crusher. Trigger for "handle this objection", "they said it's too expensive", "prep me for pushback", "objection doc for this pitch".
model: opus
sources: [chat]
adapts: realkimbarrett/objection-crusher
---

# zb-objections — ZYNTH Objection Handling

**Upstream:** `realkimbarrett/objection-crusher`.
**What ZYNTH adds:** the objections that actually come up in MM/SG agency sales, reframes rooted in ZYNTH's real edge, and dual-language response scripts. Feeds the proposal (`zb-pitch-kit`) as a pre-empt section and preps Zane for the meeting.

## Method
For every objection: **surface it before the client says it** (pre-empt in the proposal), then **reframe → evidence → script**. Never argue; reframe the frame.

## The ZYNTH objection library

**1. "It's too expensive."**
Reframe: price vs cost-of-getting-it-wrong. A cheap launch that flops costs more than the fee.
Evidence: tie to the outcome in `zb-offer`; show the tier ladder so they can self-select, not walk.
Script (EN): "Compared to what — another quote, or the cost of the launch underperforming? Let's look at what each tier returns." (MM: mirror, don't translate literally.)

**2. "We can do it in-house."**
Reframe: in-house = fixed cost + limited range; ZYNTH = events *and* video *and* bilingual creative, on demand, no headcount.
Evidence: the breadth their team can't match this quarter, the trigger deadline they can't hit alone.

**3. "You're a new/unproven agency."**
Reframe: senior operator, lean team, direct founder access — not a junior lost in a big shop.
Evidence: spec-work portfolio + the milestone-gated structure from `zb-offer` (risk sits on us, not them).

**4. "How do we know it'll work? (ROI doubt)"**
Reframe: we don't sell hope, we sell a measured plan — define the KPI up front and report against it.
Evidence: the performance-readout amplifier; the analytics discipline already in the ZYNTH stack.

**5. "The timing isn't right."**
Reframe: the trigger *is* the timing (launch/fiscal window). Waiting forfeits the moment.
Evidence: name the deadline they told us in discovery.

**6. "Let me think about it."**
Reframe: usually a hidden objection — surface which one (price / trust / internal approval) rather than chase.
Script: "Totally fair — is it the investment, the approach, or getting sign-off internally? Whichever it is, I can help with it now."

## Output
An **Objection Sheet** per pitch: the 2–3 objections most likely for *this* account (pulled from `zb-icp` fears), each with reframe + evidence + EN/MM script. A short version becomes a "You might be wondering…" block inside the proposal.

## Guardrails
- Reframe, never argue or pressure.
- Every claim must be defensible — no invented case studies or numbers.
- Bilingual scripts are transcreated, not translated.
