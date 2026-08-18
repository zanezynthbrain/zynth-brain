# The ZYNTH proposal gold standard

**Updated:** 18 August 2026
**Derived from:** the three documents the founder approved —
KPay Thadingyut (33 sections), Wave Pay Premium Launch (37), ZYNTH Agency Growth (16).

This is the depth every ZYNTH proposal ships at from now on. A five-field
summary is a *concept*, not a proposal. Do not send a concept to a client.

---

## The 16 sections

Campaign and event proposals share one spine. Sections marked ▲ are the ones
that separate a real proposal from a nice-looking one — they are also the ones
most often skipped.

| # | Section | What it must actually contain |
|---|---|---|
| 1 | **Campaign / Executive overview** | The business problem in the client's words, the objective as a number, the period, the budget envelope. |
| 2 | **Target audience profile** ▲ | **2–3 named segments**, each with demographics, location, psychographics, behaviours, **pain points** and media consumption with day-parts. Not "young urban professionals". |
| 3 | **Competitive landscape** ▲ | Who else is in this space, what they are doing now, and the specific gap we exploit. |
| 4 | **Campaign strategy** | The big idea with its name, brand positioning, key messages, tone of voice, hashtags. |
| 5 | **Channel strategy** | Each channel given a *role*, not a logo. Split of spend and why. |
| 6 | **Content plan** ▲ | Pillars with weightings, then a **week-by-week calendar** and at least two written sample drafts in the actual voice. |
| 7 | **Influencer / KOL or outreach strategy** | Named tiers, follower bands, deliverables per creator, collaboration format. |
| 8 | **Paid media plan** | Platform-by-platform budget, objective, audience build, expected CPM/CPA band. |
| 9 | **Activation / on-ground** | The physical component: what it is, where, how many, what it costs to build. |
| 10 | **Detailed budget** ▲ | An itemised table. Every line has a unit, a quantity and a rate. Subtotals must sum — check them. |
| 11 | **Timeline** | Week-by-week execution with owners and dependencies. |
| 12 | **KPIs & success metrics** | Numeric targets with the measurement source named. |
| 13 | **ROI projection** ▲ | Revenue model, and a **scenario analysis** — conservative / base / upside. |
| 14 | **Risk & mitigation** | A register: risk, likelihood, impact, the mitigation, the owner. |
| 15 | **ZYNTH fee & profit model** ▲ | Cost base, fee, and the **margin stated openly**. Must clear the 35% floor; target 40%. |
| 16 | **Why ZYNTH** | Proof, not adjectives. What we have actually produced. |

Events add: **event details** (venue, capacity, run-of-show), **vendor
requirements** (named categories with RFQ status), and **terms & conditions**.

---

## The financial law — non-negotiable

| Rule | Value |
|---|---|
| Margin floor | **35%** of revenue |
| Margin target | **40%** |
| Deposit | **50%** on signature |
| Management fee | 15–20% |
| Contingency | 10% |
| FX | 4,400 MMK / 1.35 SGD per USD (market rate) |

Margin is on **revenue**, not a mark-up on cost. A "40% fee on cost" is only
28.6% margin — that mistake has been made before and it cost real money.
Price = `cost_base / (1 - margin)`. `backend/utils/proposal_doc.py` does this
arithmetic; use it rather than a calculator.

---

## Honesty rules

- Numbers we have not verified are tagged `[UNVERIFIED]` or left blank. Never invented.
- No fabricated case studies, client names, testimonials or vendor contacts.
- Burmese is written **first** and English transcreated from it — never the reverse.
  Burmese is always typeset in Pyidaungsu, never generated inside an image or video model.
- Nothing reaches a client without founder approval.

---

## How to produce one

```
/proposal <sector> <market> <type>        (Telegram)
```
or queue it from the interface: **/command → Proposals → ASK ZYNTH TO PRODUCE**.

The writing runs on `zynth-master-proposal-writer` with this file as its
contract. Then:

```
python backend/build_vault_index.py        # it enters the library
python backend/tools/proposals_to_docx.py  # it gets a .docx
python backend/build_dashboard.py          # it appears in the interface
```
