# ZYNTH Finance Operating System

**For a founder who knows payroll and nothing else about finance.** This is the whole
finance function written as plain steps and ready-to-use templates. If you follow
this, ZYNTH's money is run properly. The CFO agent builds on this file — it never
contradicts it.

Market FX: **1 USD ≈ 4,400 MMK / 1.35 SGD** (market rate, never central-bank).
Financial law: **35% gross-margin floor · 40% target · 50% deposit · 15–20% management
fee · 10% contingency.**

---

## 1. The five numbers you must know at all times
1. **Cash in bank** (MMK + SGD) — what you actually have.
2. **Money owed to you** (unpaid invoices = accounts receivable).
3. **Money you owe** (unpaid vendors/salaries = accounts payable).
4. **This month's revenue** (invoiced) vs **this month's costs**.
5. **Gross margin %** on each live project — must be ≥35%.

If you know these five, you're in control. The CFO agent produces them; you read them.

## 2. How ZYNTH makes money (the model)
- **Retainers** (recurring monthly fee) — the stable base. **Target: 80% of revenue.**
- **Projects** (one-off campaigns/events) — the upside. **Keep under ~40%** or cash
  becomes lumpy and stressful.
- **Management fee** on media/production you run for clients: **15–20% of that spend.**

## 3. Pricing — how to quote so you never lose money
Always price **bottom-up**:
1. Add up **direct cost** (vendors + production + media-at-cost + any freelancer).
2. Add **10% contingency** on production.
3. Add ZYNTH's **management fee (15–20%)**.
4. Check the **margin**: `margin % = (price − direct cost) ÷ price`. Must be ≥35%,
   aim 40%. To hit 40%: `price = direct cost ÷ 0.60`.
5. If it won't clear 35%, don't discount silently — re-scope, or say why.

**Indicative service price anchors** (confirm per job; MMK / SGD):
| Service | Myanmar (MMK) | Singapore (SGD) |
|---|---|---|
| Social media retainer / mo | 1.5M – 5M | 1,500 – 4,000 |
| Full campaign (mid) | 8M – 30M | 6,000 – 25,000 |
| Brand identity | 3M – 12M | 3,000 – 12,000 |
| Video (1–3 cam) | 2M – 15M | 3,000 – 20,000 |
| Event (see event planner) | 30M – 500M+ | 15,000 – 150,000+ |

## 4. Quotation template (fill and send)
```
ZYNTH — Quotation
Client: __________          Date: __________   Valid: 30 days
Scope: __________________________________________
------------------------------------------------------------
Item                         Qty   Unit (MMK/SGD)   Total
------------------------------------------------------------
[line items]
------------------------------------------------------------
Subtotal (direct cost)                              ______
Contingency (10% on production)                     ______
ZYNTH management fee (15–20%)                        ______
------------------------------------------------------------
TOTAL INVESTMENT                                    ______
Payment: 50% deposit to start · 50% on delivery
(For events/large projects: 50% deposit · 30% pre-event · 20% post)
------------------------------------------------------------
```

## 5. Payment terms (the rule that protects cash)
- **50% deposit before any work starts. No deposit, no work.** This is non-negotiable
  — it funds the direct costs so ZYNTH never lends the client money.
- Balance on delivery (or the event/large-project schedule above).
- State validity (30 days) so old quotes don't bind you at stale prices.
- Late payment: a polite reminder at due date, firmer at +7 days, pause work at +14.

## 6. Invoicing (the step that actually gets you paid)
Every invoice needs: ZYNTH details, client details, invoice number (e.g. `ZY-2026-014`),
date, due date, itemised lines, subtotal, any tax, total, and **how to pay** (bank
details / KBZPay / Wave). Send the invoice the day work is agreed (for the deposit)
and the day it's delivered (for the balance). **Money owed is not money earned — chase it.**

**Invoice template**
```
INVOICE  ZY-2026-___                         Date: ____  Due: ____ (14 days)
Bill to: ______________________
------------------------------------------------------------
Description                                   Amount
------------------------------------------------------------
[deposit / balance / line items]
------------------------------------------------------------
Total due:                                    ______
Pay to: [bank / KBZPay / Wave details]
```

## 7. Bookkeeping — the simplest system that works

> **Money Out is now live data**, not just a spreadsheet: `backend/data/expenses.json`
> holds every recurring cost and `FINANCE_operating_costs.md` is the readable
> budget sheet (burn, AI credit planning, recommended top-up). In Telegram:
> `/expenses`, `/expenses burn`, `/expenses credits 15 balanced`.

Keep **one spreadsheet** (or the Drive Finance sheet) with two tabs:
- **Money In:** date · client · invoice # · amount · received? (Y/N)
- **Money Out:** date · vendor/what · amount · project it belongs to · paid? (Y/N)

Every payment in or out gets one row, same day. That's it. From this you get revenue,
costs, receivables, payables, and per-project margin. The CFO agent can maintain and
read this; you just make sure real transactions get logged.

## 8. The monthly close (30 minutes, once a month)
1. Make sure every in/out is logged for the month.
2. Revenue − costs = **profit this month**. Write it down.
3. List unpaid invoices (chase them) and unpaid bills (pay them).
4. Check retainer:project mix vs the 80:20 target.
5. Check each project cleared the 35% floor; note any that didn't and why.
The CFO agent produces this as a one-page summary; you approve it.

## 9. Payroll (the one you already know) — keep it clean
- Pay on a fixed date each month. Log every payment in "Money Out" tagged `payroll`.
- Keep each person's rate, start date, and any statutory contributions in the HR
  system (`HR_operating_system.md`), so payroll and HR always agree.
- **Never mix personal and business money.** Separate accounts. This one habit
  prevents 90% of small-business finance pain.

## 10. Cash-flow safety (don't run out of money)
- Aim to keep **at least 1–2 months of costs** in the bank as a buffer.
- Deposits fund project costs — that's why the 50% rule exists; don't start work that
  spends ZYNTH's buffer on a client's behalf.
- If a big project would drain cash before the client pays, stage it or ask for a
  larger deposit. Cash-flow, not profit, is what kills small agencies.

## 11. Tax & compliance (know it exists; get a local pro)
- **Myanmar:** commercial tax / income tax obligations apply; keep clean records and
  use a local accountant for filing. `[confirm current rules with a MM accountant]`
- **Singapore:** GST registration threshold, corporate tax, ACRA filings if you have
  an SG entity. `[confirm with an SG accountant]`
- Your job isn't to be the tax expert — it's to **keep records clean enough** that a
  cheap accountant can file fast. The bookkeeping in §7 does that.

## 12. What the CFO agent escalates to you (and nothing else)
- Any quote **below the 35% floor** (needs your yes/no).
- Any **spend commitment** or a project that risks the cash buffer.
- A client **not paying** past +14 days.
Everything else — pricing, analysis, invoices, the monthly close — it produces and
files. You decide; you don't calculate.
