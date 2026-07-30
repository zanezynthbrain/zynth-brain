# ZYNTH Event Management Operating System

**Events are one of ZYNTH's two priority revenue lines.** This is the system that runs
an event from the first enquiry to the final payment — the stages, the gates, the
SOPs, who does what, and how it plugs into the rest of ZYNTH. The *planning* is done
by the `zynth-master-event-planner` skill; **this document is the delivery machine
around it.** The live tracker is `/em` in Telegram and the Events node on the dashboard.

---

## 1. The lifecycle — 8 stages, each with a GATE
An event moves through 8 stages. Each stage has a **gate**: the one thing that must be
true before it can advance. The gate is what stops a half-baked event from eating cash.

| # | Stage | Gate to ENTER it | Who / what does the work |
|---|-------|------------------|--------------------------|
| 1 | **enquiry** | A request came in | Respond in **2 hours** (Speed Moat), book a brief |
| 2 | **qualified** | Brief captured: client, type, date, guests, budget band, market, objective | You + the client (a call) |
| 3 | **proposed** | A complete **costed** proposal + quote sent | `zynth-master-event-planner` skill builds it |
| 4 | **confirmed** | Client agreed **AND 50% deposit received** | Finance issues the deposit invoice |
| 5 | **preproduction** | Deposit banked; run-of-show drafted; suppliers being booked | Ops + `zynth-vendor-finder` |
| 6 | **live** | Run-of-show FINAL; all suppliers confirmed; permits/safety/contingency ready | Event crew on the day |
| 7 | **wrap** | Event delivered; teardown; final invoice issued | Ops + Finance |
| 8 | **closed** | Final payment received; post-event report sent; upsell logged | You + the self-improvement loop |

(A dead lead goes to **lost** — and the reason is logged, so the system learns.)

**The golden gate: no deposit → not confirmed → no supplier spend.** This single rule
protects ZYNTH's cash. The `/em` tracker enforces it — it warns you if you try to move
to confirmed/preproduction without the deposit recorded.

---

## 2. The process, end to end (what actually happens)
1. **Enquiry lands** → you register it: `/em add KBZ Bank | product launch | 2026-11-14 | 300 | 120M MMK`. Reply to the client within 2 hours.
2. **Qualify it** → one call to lock objective, guest profile, date, budget band, market. `/em stage E001 qualified`.
3. **Plan + price it** → run the event-planner skill (`/event KBZ product launch` or ask in Claude). It produces the complete plan: concept → run-of-show → suppliers → itemised budget → funding model → ROI. Send it. `/em stage E001 proposed`.
4. **Win it** → client says yes; **Finance issues the 50% deposit invoice**; when it's in, `/em deposit E001 paid` then `/em stage E001 confirmed`.
5. **Pre-production** → `/em stage E001 preproduction`. Now the real build: finalise the run-of-show, RFQ + book every supplier (≥2 quotes each), secure permits/insurance/safety, confirm crew, brief every vendor.
6. **Event day (live)** → `/em stage E001 live`. Crew call, soundcheck, run the show to the ROS, manage VIPs and contingencies, capture content.
7. **Wrap** → `/em stage E001 wrap`. Teardown, settle suppliers, issue the balance invoice, draft the post-event report (results vs objective).
8. **Close** → `/em stage E001 closed`. Send the report, log the upsell/next event, and the self-improvement loop captures what to do better next time.

At any point: `/em` shows the whole pipeline, `/em show E001` shows one event with its
gate + checklist, `/em next` shows upcoming events and what's due.

---

## 3. Roles — who owns what (AI does the work, you decide)
- **Enquiry & client relationship** → you (MD), backed by the account-manager skill.
- **Plan & price** → the event-planner skill (concept, run-of-show, budget, funding).
- **Sourcing** → the vendor-finder skill + ZYNTH supplier/venue DB (RFQs, comparisons).
- **Money** → the Finance system (`FINANCE_operating_system.md`): deposit invoice,
  margin check (≥35% floor), balance invoice, post-event P&L.
- **On-the-day** → the crew roles in the run-of-show (event director, stage manager,
  production manager, registration, hospitality, technical, security).
- **Escalation to you** → only real owner-decisions: confirming a booking, committing
  vendor spend, sign-off on a sponsor/ticket price, a client-facing send.

---

## 4. The SOPs (the standards that make it repeatable)
**Deposit SOP.** 50% deposit before any work or supplier commitment. No deposit → the
event stays at `proposed`. The balance follows the schedule (e.g. 30% pre-event, 20%
post). Sponsors pay 50–100% before the event.

**Sourcing SOP.** Every material line gets **≥2 quotes**. Never invent a vendor or a
contact — unknown = "to source". Use the lower quote for the margin-floor check, the
realistic quote for the client price. Book only after the deposit is in.

**Run-of-show SOP.** Minute-by-minute from crew call to load-out: time · segment ·
action · owner · cue. **Every line has an owner and a cue** — no owner means it won't
happen. The ROS must be FINAL before the event goes `live`.

**Budget-control SOP.** Bottom-up itemised budget with a **10% contingency** (non-
optional for events) and the **15–20% ZYNTH fee**. Margin must clear **35%** (aim 40%).
Track actual-vs-budget; the wrap stage reconciles it into a post-event P&L.

**On-the-day SOP.** Crew call + soundcheck first. Registration flow, VIP handling,
speaker/talent management, comms protocol, incident escalation, and a **Plan B for
weather, power, and a no-show speaker**. Capture photo/video for the recap.

**Compliance SOP.** Permits (venue, municipal, entertainment, F&B, filming), insurance,
fire/first-aid, and — for video — the 2025 Motion Picture Law lead time. Bilingual
signage (Burmese Unicode/Pyidaungsu + English), Halal/veg F&B, Yangon traffic factored
into the ROS.

---

## 5. How it connects to the rest of ZYNTH
- **Planning depth** → `zynth-master-event-planner` skill (the full plan + run-of-show).
- **Real rates** → `backend/knowledge/22_myanmar_event_landscape.md` + the event
  planner's `production-costs.md` (Yangon venue/AV/F&B/crew bands, event-type budgets).
- **Money** → `docs/departments/FINANCE_operating_system.md` (invoices, margin, P&L).
- **Sourcing** → `zynth-vendor-finder` + the supplier/venue databases.
- **Tracking** → `/em` (Telegram) and the **Events** node on the Command Center.
- **Learning** → every `lost` reason and post-event lesson feeds the self-improvement
  loop (`/improve`), so the next event is run better.

---

## 6. Quick command reference (`/em`)
```
/em                                  the whole event pipeline
/em add Client | type | date | guests | budget    register an event
/em show E001                        one event + its gate & checklist
/em stage E001 confirmed             advance a stage (gate-checked)
/em deposit E001 paid                record the 50% deposit
/em next                             upcoming events + what's due
```
Plan any registered event with the event-planner skill (`/event <client> <type>` or ask
in Claude). The tracker keeps the delivery honest; the skill makes the plan world-class.
