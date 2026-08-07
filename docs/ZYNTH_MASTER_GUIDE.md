<!-- TEMPLATE -->
<!-- Human reference. The knowledge loader skips this so it doesn't eat agent context. -->

# ZYNTH — Master Guide / မာစတာ လမ်းညွှန်

> Everything that exists, where it lives, and how to use it.
> အားလုံး ဘယ်မှာရှိလဲ၊ ဘယ်လိုသုံးရမလဲ။
> Last updated 2026-08-07.

---

# PART 1 — Where everything is stored / သိမ်းဆည်းမှု စနစ်

Four places. Each has **one** job. Confusing them is how work gets lost.
နေရာ လေးခု ရှိပါတယ်။ တစ်ခုချင်းစီမှာ တာဝန်တစ်ခုစီ ရှိပါတယ်။

| Where | Job | The rule |
|---|---|---|
| **GitHub** (`zanezynthbrain/zynth-brain`) | The single source of truth. Code, skills, knowledge, committed data. | If it isn't in GitHub, it doesn't exist. |
| **Railway** (`fabulous-bravery`) | The runtime. Runs the Telegram bot + scheduler 24/7. Deploys on merge to `main`. | Its disk is **ephemeral** — anything written there is lost on redeploy unless it's in the pool. |
| **Claude Code** | The workshop. Where the system gets built and changed. | Sessions are temporary. Work must be committed and pushed or it vanishes. |
| **Obsidian** | Your reading surface. The narrative, not the database. | Points at the repo's `vault/` folder only. |

**မြန်မာလို —**
- **GitHub** = အမှန်တရား သိမ်းရာနေရာ။ repo ထဲမရှိရင် မရှိသလိုပါပဲ။
- **Railway** = bot အလုပ်လုပ်နေတဲ့ server။ `main` ကို merge လုပ်မှ deploy ဖြစ်တယ်။ ဒီ server ရဲ့ disk က redeploy တိုင်း ပျက်တာမို့ အရေးကြီးတဲ့ data ကို repo ထဲ ပြန်သိမ်းရပါတယ်။
- **Claude Code** = စနစ်ကို တည်ဆောက်တဲ့ အလုပ်ရုံ။ commit + push မလုပ်ရင် ပျောက်သွားပါမယ်။
- **Obsidian** = သင်ဖတ်ဖို့ နေရာ။ `vault/` ဖိုလ်ဒါကိုပဲ မြင်ပါတယ်။

### How data actually survives — the pool pattern
Railway's disk resets on every deploy. So anything that must survive is written
to **`backend/outputs/proposal_pool/`** and committed back to GitHub by a daily
GitHub Action (07:00 SGT). That folder holds: leads, suppliers, venues, brand
profiles, the publish queue, expenses, outcomes, and `/note` captures.

**Everything else in `outputs/` is disposable** — generated .docx, PNGs, review
boards. They regenerate from the committed data.

**မြန်မာလို —** Railway က redeploy လုပ်တိုင်း file တွေ ပျက်တယ်။ ဒါကြောင့် မပျက်စေချင်တဲ့
data အားလုံးကို `outputs/proposal_pool/` ထဲ ရေးပြီး GitHub ကို နေ့စဉ် အလိုအလျောက်
ပြန်တင်ပါတယ်။

### The flow
```
Claude Code  →  git push  →  GitHub branch  →  PR  →  main
                                                       ↓
                                              Railway auto-deploys
                                                       ↓
                                          Telegram bot (you use it)
                                                       ↓
                                  data → outputs/proposal_pool/
                                                       ↓
                              daily Action commits it → GitHub
                                                       ↓
                              Obsidian Git pulls → vault/ (you read it)
```

---

# PART 2 — The two Claude Code projects / Claude Code နှစ်ခု ဆက်သွယ်ခြင်း

You have two sessions on the same repo: **"2nd Multi-agent content and design
system"** (this one) and **"Main - ZYNTH multi-agent marketing framework."**

**They are already connected — through git.** That is the correct mechanism, and
there is no separate "link" to switch on. What matters is the discipline:

1. **Both must `git pull` before starting work.** Otherwise you get two versions
   of the same file and a merge conflict later.
2. **One branch per session.** Never two sessions on the same branch.
3. **Merge to `main` often** — small merges, not one giant one at the end.
4. **`CONTEXT.md` is the shared memory.** Both sessions read it on start
   (`CLAUDE.md` enforces this). Anything one session decides, the other learns
   from that file.
5. **Handoff docs** (`docs/handoff/`) carry decisions between sessions — exactly
   how the 2026-08-06 back-office work reached this session.

**မြန်မာလို —** Claude Code နှစ်ခုဟာ GitHub repo တစ်ခုတည်းကို သုံးနေတာမို့
**ဆက်သွယ်ပြီးသား** ဖြစ်ပါတယ်။ သီးခြား ချိတ်ဆက်စရာ မလိုပါဘူး။ လိုအပ်တာက စည်းကမ်းပါ —
အလုပ်မစခင် `git pull` လုပ်ပါ၊ session တစ်ခုစီ branch တစ်ခုစီ သုံးပါ၊ `main` ကို
မကြာခဏ merge လုပ်ပါ၊ ဆုံးဖြတ်ချက်တိုင်းကို `CONTEXT.md` မှာ ရေးထားပါ။

> **The one rule that prevents pain:** never let two sessions edit the same file
> on different branches at the same time. Split by area — one takes the backend,
> the other takes skills and docs.

---

# PART 3 — The full skill list / စွမ်းရည် စာရင်း

**34 skills**, all in `.claude/skills/` (repo-versioned — they travel with every
clone). Call one by typing `/skill-name` or just describing the task.

### Back-office — the sales spine (`zb-` + finance)
Chain them in order: **icp → offer → quote → objections → pitch-kit.**

| Skill | Use it for |
|---|---|
| `zb-icp` | Define and score a prospect before outreach |
| `zb-offer` | Build a costed, compelling offer |
| `zb-objections` | Pre-empt "too expensive", "we'll do it in-house" (EN + MM) |
| `zb-pitch-kit` | Assemble the deck, one-pager, demo script |
| `yadana-finance` | **YADANA** — quote, margin check, P&L, cashflow, invoicing |

### Strategy & planning
`zynth-master-campaign-planner` · `zynth-master-event-planner` ·
`zynth-master-proposal-writer` · `zynth-brand-strategist` ·
`zynth-content-strategist` · `zynth-campaign-planner` ·
`zynth-campaign-requirements` · `zynth-project-manager` ·
`zynth-sponsorship-value` *(new — sponsorship tiers + ROI)*

### Creative & production
`zynth-creative-director` · `zynth-art-director` · `zynth-copywriter` ·
`zynth-creative-video-director` *(the deep one — camera, grading, editing)* ·
`zynth-video-producer` · `zynth-3d-production` *(new — booths, stages)* ·
`zynth-tactical-prompts` *(new — prompt library)*

### Growth, BD & analysis
`zynth-bd-researcher` · `zynth-bd-pitch-prep` · `zynth-market-researcher` ·
`zynth-competitor-analyst` · `zynth-paid-media-specialist` ·
`zynth-seo-specialist` · `zynth-analytics-specialist` ·
`zynth-social-media-manager`

### Client & operations
`zynth-account-manager` · `zynth-event-manager` · `zynth-vendor-finder` ·
`zynth-pitch-packager` · `graphify`

---

# PART 4 — The bot commands / Telegram အမိန့်များ

The bot is the interface you use daily. **34 commands.** The ones that matter:

### Content & design
| Command | What it does |
|---|---|
| `/content <brand> <8\|10\|16\|30>` | A full month: strategy + calendar (MM+EN) + visual system + design specs |
| `/brandkit add <details>` | Store a brand + its target audience so agents stop guessing |
| `/review <brand>` | **QC board** — artwork + both languages + automatic checks |
| `/schedule <brand>` | Approve each post, then schedule to Facebook + Instagram |
| `/meta check` | Test the Meta connection |

### Money
| Command | What it does |
|---|---|
| `/expenses` · `/expenses burn` | What ZYNTH pays monthly (~US$60) |
| `/expenses credits 15 balanced` | Credits needed for a 15s film |
| `/cost` · `/costaudit` | API spend vs the daily cap |

### Learning (new)
| Command | What it does |
|---|---|
| `/outcome P04 post engagement_rate=4.2` | Record what really happened |
| `/outcome verify P04` | Confirm against the real dashboard |
| `/outcome` | Performance vs outside benchmarks |
| `/outcome learn` | Push measured misses into every agent's prompt |

### Documents & events
`/proposal <brief>` · `/event <brief>` · `/video <brief>` · `/proposals` ·
`/generate` · `/venue` · `/vendor` · `/lead` · `/prospects` · `/em`

### Running the agency
`/brief` · `/report` · `/status` · `/dashboard` · `/task` · `/scorecard` ·
`/audit` · `/note` · `/kb` · `/mirror` · `/push` · `/fx` · `/improve` ·
`/roundtable` · `/switch` · `/quiet` · `/active`

---

# PART 5 — How the system learns / စနစ်က ကိုယ်တိုင် သင်ယူပုံ

There are now **two loops**. One grades its own homework; the other checks
reality. You need both.

### Loop 1 — internal (already existed)
```
work produced → Critic scores it → /revise verdicts → utils/mistakes.py
                                                            ↓
                              recurring mistakes → utils/lessons.py
                                                            ↓
                                        injected into every agent prompt

approved work scoring highest → utils/bestof.py → becomes the few-shot exemplar
```

### Loop 2 — external (new: `utils/outcomes.py`)
```
real result (engagement, win/loss, actual cost)
        ↓  /outcome P04 post engagement_rate=2.1
compared to an external BENCHMARK (each one names its source)
        ↓
verdict: beat / met / missed
        ↓  3+ verified misses on the same metric
/outcome learn  →  a lesson  →  every agent prompt
```

**Why this matters.** Before, the system could only compare itself to itself —
it would happily produce beautiful work that nobody engaged with and score it
highly. Now a metric that misses its benchmark three times becomes a written
instruction the agents read on the next run.

**မြန်မာလို —** အရင်က စနစ်ဟာ ကိုယ့်ကိုကိုယ်ပဲ အမှတ်ပေးနိုင်တာမို့ "လှတယ်၊ ဒါပေမယ့်
ဘယ်သူမှ မကြည့်ဘူး" ဖြစ်နိုင်ပါတယ်။ အခုတော့ **တကယ့်ရလဒ်** ကို ပြင်ပ စံနှုန်းနဲ့
နှိုင်းယှဉ်ပြီး၊ သုံးကြိမ် ဆက်တိုက် စံနှုန်းအောက် ရောက်ရင် အေးဂျင့်တိုင်းရဲ့
ညွှန်ကြားချက်ထဲ အလိုအလျောက် ထည့်ပေးပါတယ်။

**The discipline it needs from you:** the loop is only as good as the numbers you
feed it. One minute a week — read the real figures off Meta Business Suite and
type them in. Unverified numbers never count toward a benchmark, by design.

---

# PART 6 — n8n vs what we built / n8n နဲ့ ဘယ်ဟာ ပိုကောင်းလဲ

**Wrong question — they do different jobs.** The honest answer is that you will
probably end up using both, and knowing which is which saves you months.

| | **n8n** | **ZYNTH-brain (what we built)** |
|---|---|---|
| What it is | A visual workflow automation tool — boxes and arrows | A multi-agent system with domain knowledge |
| Best at | *Plumbing*: when X happens, do Y. Reliable, repeatable, visible | *Judgement*: what should we say, what should this cost, is this good enough |
| Example it wins | "New Google Form entry → create Trello card → send Slack message" | "Write a month of Burmese content for a Yangon F&B brand at 40% margin" |
| Interface | Excellent visual editor | Telegram + a basic dashboard |
| Non-technical editing | Yes — drag boxes | No — needs Claude Code |
| Knows your business | No | Yes — R1–R5, MM/SG rates, vendors, brand voice |
| Cost | Free self-hosted (~US$5 VPS) or ~US$24/mo cloud | ~US$60/mo total stack |

**The verdict:** n8n cannot do what ZYNTH-brain does. It has no judgement — it
runs steps you defined in advance. Asking n8n to write Burmese ad copy at the
right margin is asking a spreadsheet to have taste.

But ZYNTH-brain is **worse than n8n at plumbing**. Connecting Gmail → Sheets →
Slack → HubSpot on a schedule, with retries and a visual log, is exactly what
n8n is for, and doing it in Python costs you a week.

**မြန်မာလို —** n8n က **အလိုအလျောက် ချိတ်ဆက်ရေး** (X ဖြစ်ရင် Y လုပ်) အတွက် အကောင်းဆုံးပါ။
ကျွန်တော်တို့ဆောက်ထားတဲ့ စနစ်ကတော့ **ဆုံးဖြတ်ချက်ချရေး** (ဘာရေးမလဲ၊ ဘယ်လောက်ယူမလဲ၊
ကောင်းပြီလား) အတွက်ပါ။ နှစ်ခုက အလုပ်မတူပါဘူး။ n8n က မြန်မာလို ကြော်ငြာ မရေးနိုင်သလို၊
ကျွန်တော်တို့စနစ်ကလည်း app ဆယ်ခု ချိတ်ဆက်ဖို့ n8n လောက် မလွယ်ပါဘူး။

**Recommendation:** don't replace anything. If a plumbing job appears — syncing
tools, moving files, scheduled notifications — put n8n in front of the bot and
let it call the bot's HTTP endpoint. Keep the judgement in ZYNTH-brain.

---

# PART 7 — The interface problem / Interface အားနည်းချက်

You're right, and it's the biggest remaining weakness. Today you have:
Telegram (good for approvals, bad for reading long documents), a basic HTML
dashboard, the QC review board, and Obsidian for reading.

**Three options, honestly compared:**

| Option | Effort | What you get | Cost |
|---|---|---|---|
| **A. Improve the existing dashboard** | ~2 days | One web page: pipeline, approvals, calendar, outcomes, costs. Already served on Railway | US$0 |
| **B. Retool / Appsmith** (internal-tool builder) | ~3 days + learning | Drag-and-drop admin UI, proper tables and forms | Free tier, then ~US$10/user/mo |
| **C. Proper web app** (Next.js) | 2–3 weeks | Exactly what you want, client-facing capable | US$0 hosting, high time cost |

**Recommendation: A now, C later.** The dashboard already exists and is already
served publicly by the bot — extending it is the fastest path from "no interface"
to "a page I check every morning." Build C only when a *client* needs to log in.

**မြန်မာလို —** Interface အားနည်းတာ မှန်ပါတယ်။ အခုရှိတဲ့ dashboard ကို တိုးချဲ့တာ
အမြန်ဆုံးနဲ့ အသက်သာဆုံးပါ (၂ ရက်ခန့်)။ Client တွေ ဝင်သုံးဖို့ လိုလာမှ web app
အပြည့်အစုံ ဆောက်သင့်ပါတယ်။

---

# PART 8 — How to actually use this, week to week

**Monday (10 min)** — `/brief` · `/scorecard` · `/expenses burn`
**When a lead appears** — `zb-icp` → `zb-offer` → `yadana-finance` → `zb-objections` → `zb-pitch-kit`
**Monthly per client** — `/content <brand> 16` → `/review <brand>` → fix → `/schedule <brand>` → approve each post
**After posting (weekly, 1 min)** — `/outcome <ref> post engagement_rate=X` → `/outcome verify <ref>`
**Monthly (5 min)** — `/outcome` → `/outcome learn` → `/improve`
**End of any build session** — update `CONTEXT.md`, `python backend/tools/refresh_bridge.py`, commit, push, merge to main

---

# PART 9 — What is still missing (be honest about it)

1. **No live Meta tokens** — publishing is dry-run until `META_ACCESS_TOKEN`,
   `META_PAGE_ID`, `META_IG_USER_ID` and `ZYNTH_PUBLIC_URL` are set.
2. **No OpenArt credits** — 5 left. ~8,700 needed for a 3-film portfolio slate.
3. **No finance workbook yet** — YADANA §10 spec exists; the .xlsx isn't built.
   Build it **banded** (green ≥40 / amber 35–39.9 / red <35), not a flat 40% block.
4. **No real outcome data** — the learning loop is built but has nothing to
   learn from until you type in the first real numbers.
5. **Interface** — see Part 7.
6. **Client names unverified** — the September plan's P05/P09 need written
   permission before publishing.
