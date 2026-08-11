<!-- TEMPLATE -->
<!-- Generated mirror — the knowledge loader skips this file on purpose. -->
---
generated: true
source: docs/departments/FINANCE_operating_costs.md
mirrored: 2026-08-07 09:44
---

> **Generated mirror of `docs/departments/FINANCE_operating_costs.md`.** Edit the source in the repo, not this
> file — the next `/mirror` overwrites whatever is here.

# ZYNTH — Operating Costs & AI Production Budget

> The "Money Out" list from `FINANCE_operating_system.md` §7, kept as real data
> in `backend/data/expenses.json` and readable in Telegram with `/expenses`.
> Recorded 2026-08-05 from the MD. **Amounts marked TBC are unverified** — the
> standing rule applies: an agent may not present them as fact.

---

## 1. Monthly burn — what it costs to stay switched on

| Item | Amount | Cadence | Status |
|---|---|---|---|
| Claude Pro (Claude Code) | US$20.00 | monthly | ⚠️ TBC — confirm Pro vs Max |
| Anthropic API (agent runtime) | US$30.00 | usage ceiling | ⚠️ TBC — this is the CAP, not actual |
| OpenArt (Starter) | *unknown* | monthly | ⚠️ TBC — price not readable from here |
| Domain — zynth.asia | *unknown* | yearly | ⚠️ TBC — from the registrar invoice |
| Mobile data + Wi-Fi | US$5.00 | monthly | ✅ MD-reported |
| Railway (bot hosting) | US$5.00 | monthly | ⚠️ TBC — not named by the MD, but the bot runs on it |

**Confirmed: US$5.00/month · Estimated: US$55.00/month · Total: ~US$60/month**

Two figures are deliberately blank rather than guessed: OpenArt's plan price and
the .asia domain renewal. `openart.ai` is blocked from this environment, so any
number I put there would be invention. Fill them in and the burn becomes real:

```
/expenses verify "OpenArt (Starter)" 14
/expenses verify "Domain — zynth.asia" 18
```

**The Anthropic API line needs care.** US$30 is the monthly *ceiling* already
agreed (S$40/month, with a S$5/day cap enforced in `cost_tracker.py`). Actual
spend is lower — `/cost` and `/costaudit` report the truth. Budgeting at the cap
is the safe way to plan; reporting at the cap would be wrong.

At ~US$60/month, the whole agency infrastructure costs less than a single
freelance design day. That is the number to keep in front of a client who thinks
an agency retainer is expensive.

---

## 2. AI production credits — stock, not subscription

Credits are inventory. They belong in "Money Out" as **one-off purchases**, not
in the recurring burn, and they should be bought against a specific slate of
films rather than topped up reactively.

### The rule most people get wrong

**Credits scale with SHOT COUNT, not runtime.** Every shot is a separate
generation billed at a 5-second minimum, even though only ~2 seconds reaches the
cut. So a fast-cut 15-second film costs *more* than a slow 15-second film.

A 15s commercial at commercial pacing = ~8 shots = 40 generated seconds.

### Cost per film (pipeline: still plate → animate the plate)

| Film | Tier | Shots | Credits |
|---|---|---|---|
| 15s | lean (PixVerse throughout) | 8 | **972** |
| 15s | balanced (2 hero + 6 volume) | 8 | **2,524** |
| 15s | premium (Seedance throughout) | 8 | **4,752** |
| 30s | balanced | 15 | **4,084** |
| 30s | premium | 15 | **8,910** |

All figures include a **×1.35 retake factor**. Budgeting one attempt per shot is
the most common way an AI film runs over — shots fail, and the second attempt
costs the same as the first.

### Recommended slates

| Goal | Slate | Credits |
|---|---|---|
| One flagship portfolio piece | 1 × 15s premium | **4,752** |
| Portfolio for all three services | 3 × 15s balanced | **7,572** |
| Volume/social library | 6 × 15s lean | **5,832** |
| Full launch slate | 3 × 15s balanced + 1 × 30s premium | **16,482** |

**My recommendation: buy for the 3 × 15s balanced slate — ~7,600 credits, plus
a ~15% buffer ≈ 8,700.**

That gives you one portfolio film per service line — video production, social
media management, event management — which is exactly what a prospect asks to
see. Balanced tier puts the hero model only on the two shots that carry each
idea and runs the rest at volume rate, which is where the quality-per-credit
actually sits. Premium on all eight shots costs nearly double for a difference
most viewers will not see on a phone.

**I cannot tell you the dollar cost** — OpenArt's pricing page is blocked from
this environment, and the Starter plan's included credits and top-up pack prices
aren't exposed through the API. Take 8,700 credits to your billing page, find
the pack that covers it, and log it:

```
/expenses add "OpenArt credit top-up" <amount> one_off
```

### Where the last balance went

The account ran 3,170 → 5 credits. Four stills I generated account for ~160 of
that at list rates. The remainder is consistent with the video clips in your 45s
Samsung film — roughly 9 clips at hero rates. That is the lesson in the table
above made concrete: **one 45-second film at hero tier consumes a whole Starter
balance.** Tier the shots or the credits vanish into B-roll.

---

## 3. What is deliberately NOT in this budget

The MD has no production team yet, so the model is **edit-only, AI-generated**.
That removes, for now:

- Crew day rates (director, DP, gaffer, sound) — `23_mm_video_production_rates.md`
- Equipment rental
- Talent and location fees

**Keep those rates on file anyway.** When a client asks for a filmed shoot, the
answer is a real quote from those tables, not a refusal — ZYNTH is producer-led
and outsources the crew. The AI pipeline is how the *portfolio* gets built, not
a claim that ZYNTH never films.

---

## 4. Monthly close — the two-minute version

1. `/expenses burn` — is the total what you expected?
2. `/cost` — actual API spend vs the cap.
3. Any TBC still unverified after a month? Verify it or delete the line.
4. Credits left vs films still to make. Top up **before** the slate starts, not
   mid-film — a film paused halfway loses its look continuity.
5. Log every top-up as `one_off` so the recurring burn stays honest.
