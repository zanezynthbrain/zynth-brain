# Myanmar Market Researcher — How It Works (Flow)

An always-on agent that finds **potential business clients** in Myanmar, scores
each for fit, stores them, shows them to you, and tells you what's new — every
day, on its own, plus on demand when you ask.

> It is **not** named after any person or brand — it's a function: *research
> Myanmar businesses → qualify → notify*. Quality over volume: every prospect is
> a real company with a reason to need ZYNTH, deduplicated and fit-scored.

---

## 1. Where the data comes from (seek)

| Source | What it gives |
|---|---|
| **Seed set** (`backend/data/prospects_seed.json`) | ~50 well-known Myanmar companies across every target sector — the DB is never empty. |
| **The researcher agent** (Claude) | Knows the Myanmar landscape (banks, telcos, FMCG, retail, property, hospitals, universities, auto, hotels, conglomerates) and produces new, real companies each run. |
| **Best-effort live web research** (`utils/webresearch.py`) | Current signals pulled at run time (never blocks — if the network is limited it just uses the model's knowledge). |
| **You** | `/scout <sector>` to point it at any sector; graduate a prospect into a real lead with `/lead add`. |

**Target sectors** (it rotates one per day): Banking & Fintech · Telecom & Tech ·
FMCG · Retail & Malls · Real Estate · F&B chains · Healthcare · Education · Auto ·
Hospitality · Insurance · Manufacturing · Construction · Beauty & Lifestyle ·
Logistics & E-commerce · Energy · Agriculture · NGO/Gov.

**Rule:** it never invents a phone number or email. Unknown contacts stay blank
and the record is `verified: false` — confirming a contact is human work.

---

## 2. Where the data goes (store)

- **File:** `backend/outputs/proposal_pool/prospects.json`
- Committed by the daily pool workflow, so it **survives Railway redeploys** — the
  repo is the durable database.
- **Each record:** company · industry · sub-sector · location · size · **why_fit** ·
  **fit_score (1–5★)** · service_fit · website/facebook · source · status · created_at.
- **Deduplicated** automatically by normalised company name — the same business is
  never added twice, no matter how many times research runs.
- **Status flow:** `new → reviewing → contacted → qualified → dropped`. Once you
  actually work a prospect, add it to the BD pipeline with `/lead add` (that's the
  active-deal database in `leads.json`).

---

## 3. How you see it (view — clearly)

| Where | What you see |
|---|---|
| **Telegram `/prospects`** | Stats (total · hot ★★★★+ · added today/this week) + the hottest prospects. `/prospects fintech` searches by sector/keyword. |
| **Dashboard** | A **Prospects** KPI tile + the BD department shows `N prospects · M leads`. Everything updates live. |
| **The file** | `prospects.json` — open it anywhere, or hand it to any AI/tool. |

---

## 4. Running by itself (daily automation)

- **06:30 Yangon, every day** the scheduler runs the researcher on that day's
  sector (rotating), dedupe-appends the new finds, and sends you a digest:
  > 🔎 Market Researcher — Telecom & Technology
  > +18 new prospects today · 4 dupes skipped · DB now 214
  > Top new: • Company (5★) — why they fit …
- Delivered to **Telegram *and* email**, and logged to the dashboard activity feed.
- Over ~18 days it cycles every sector, then goes deeper — the list **compounds**
  into the thousands as long as the API has credit. (First run with no credit just
  loads the seed set and tells you.)

## 5. On demand (type to proceed)

- **`/scout`** — research today's sector right now.
- **`/scout fintech`** (or any sector) — research a sector you choose, on the spot.
- **`/prospects`** — see the whole database / search it.
- It appends + dedupes + replies with the top new finds immediately.

---

## 6. Honest note on "thousands"

Thousands of **solid** prospects come from the DB **compounding daily** — not from
dumping a scraped list of noise (that's the "useless data" you don't want). The
seed gives you a real, high-value start today; the daily engine grows it with
deduped, fit-scored, real companies. The two things that pace it: **Anthropic API
credit** (the researcher's brain) and, for live web signals, outbound network.
Verifying contact details is the human step before outreach.

---

## Files

- `backend/utils/prospects.py` — the database (store, dedupe, search, stats)
- `backend/data/prospects_seed.json` — the seed set + sources
- `backend/agents/market_researcher.py` — the researcher agent
- `backend/scheduler.py` — `collect_prospects()` + the 06:30 daily job
- `backend/telegram_bot.py` — `/prospects`, `/scout`
- `backend/utils/dashboard.py` — the Prospects tile + BD headline
