
## graphify
# /graphify
## Usage
## What graphify is for
## What You Must Do When Invoked
### Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)
### Step 1 - Ensure graphify is installed
# Detect the correct Python interpreter (handles uv tool, pipx, venv, system installs)
# 1. uv tool installs — most reliable on modern Mac/Linux
# 2. Read shebang from graphify binary (pipx and direct pip installs)
# 3. Fall back to python3
# Write interpreter path for all subsequent steps (persists across invocations)
# Save scan root so `graphify update` (no args) knows where to look next time
### Step 2 - Detect files
### Step 2.5 - Video and audio (only if video files detected)
### Step 3 - Extract entities and relationships
#### Part A - Structural extraction for code files
#### Part B - Semantic extraction (parallel subagents)
# Only content files go to semantic extraction. Code is already covered structurally
# by the AST pass (Part A); flattening every category here makes subagents re-read
# every source file (#1392). Video is transcribed to a document in Step 2.5 first.
# Always (re)write the cache file: write hits, else DELETE any leftover from a prior
# run so Part C never merges a stale .graphify_cached.json (#1392).
# Then for chunk N: CHUNK_PATH="${PROJECT_ROOT}/graphify-out/.graphify_chunk_0N.json"
#### Part C - Merge AST + semantic into final extraction
# Merge: AST nodes first, semantic nodes deduplicated by id
### Step 4 - Build graph, cluster, analyze, generate outputs
# root= mirrors the --update runbook (#1361): relativize source_file to the same
# base so the full build and incremental --update never drift apart on re-extract.
# Guard BEFORE any write: an empty extraction must not clobber a good graph.json /
# GRAPH_REPORT.md / analysis sidecar. Check immediately after build (#1392).
# Placeholder questions - regenerated with real labels in Step 5
# Export FIRST and honor the #479 shrink-guard: to_json returns False (writing
# nothing) when the new graph is smaller than the existing graph.json. Only write
# GRAPH_REPORT.md + the analysis sidecar when the graph was actually written, so
# they never describe a graph that graph.json doesn't contain (#1392).
### Step 4.5 - Graph health check (read-only integrity gate)
### Step 5 - Label communities
# root= as in Step 4 / the --update runbook (#1361) — same base for node-key parity.
# LABELS - replace these with the names you chose above
# Regenerate questions with real community labels (labels affect question phrasing)
### Step 6 - Generate Obsidian vault (opt-in) + HTML
# or with custom dir: graphify export obsidian --dir ~/vaults/my-project
# or: graphify export html --no-viz
### Steps 6b-8 - Wiki, Neo4j, FalkorDB, SVG, GraphML, MCP, benchmark (only on their flags)
### Step 9 - Save manifest, update cost tracker, clean up, and report
# Save manifest for --update
# In --update mode, 'all_files' carries the full corpus; 'files' is the changed
# subset. Full-rebuild mode populates only 'files', so the fallback handles that.
# root= relativizes the manifest keys to the scan root (same base as the build),
# so the on-disk manifest is portable across clones/machines and a later --update
# matches cached files instead of missing every one (#1417).
# Only stamp semantic files (docs/papers/images) that ACTUALLY produced output:
# a detected file whose chunk failed or was omitted must stay unstamped so the
# next --update re-queues it, otherwise it is marked done and its content is lost
# forever (#2015). This mirrors the library extract path exactly
# (cli._stamped_manifest_files + clear_semantic + scan_corpus); do not stamp the
# raw corpus. Code files are always stamped (AST is deterministic); only semantic
# types are gated on output.
# Files dispatched this run (the changed subset) but NOT stamped above still carry
# a stale semantic_hash from a prior run; clear it so detect_incremental re-queues
# them instead of reading them as unchanged (#1948).
# scan_corpus = the RAW full corpus (not the stamp-filtered subset) so in-root
# files newly excluded since last run are dropped rather than masquerading as
# deletions; untouched files' prior rows are still preserved (#1908).
# Update cumulative cost tracker
## Interpreter guard for subcommands
## For --update and --cluster-only
## For /graphify query
## For /graphify add and --watch
## For the commit hook and native CLAUDE.md integration
## Honesty Rules

## yadana-finance
# YADANA — ZYNTH Finance Controller & Finance Operating System
## 1. Scope (what YADANA owns)
## 2. The Quoting Engine (the core method)
## 3. R1–R5 Financial Law — RECONCILED (the repo's text, verbatim)
### 3.1 Margin banding (how R1 is applied)
### 3.2 Quoting discipline (YADANA's own rules — not R-law)
## 4. Rate Card (structure)
## 5. Project P&L (per job, always)
## 6. Cashflow & Runway
### 6.1 The ledger already exists — call it, don't restate it
### 6.2 Cashflow
## 7. Invoicing & Collections (SOP)
## 8. KPIs (what YADANA reports)
## 9. Currency & market reality
## 10. The financial model — xlsx spec (build target)
1. **Rate Card** — roles, day-rates, tier prices, retainer bands (inputs).
2. **Vendor Benchmarks** — standard costs pulled from the vendor DB.
3. **Quote Builder** — enter a job → auto cost build-up (DC+LC+OH) → markup → price → margin check vs R1. Red flag if < floor.
4. **Project P&L** — quoted vs actual per job; gross profit + margin %.
5. **Cashflow (13-week)** — inflows/outflows, closing cash, runway.
6. **Dashboard** — the KPIs in §8, auto-fed from the sheets.
## 11. Guardrails

## zb-icp
# zb-icp — ZYNTH ICP & Prospect Definition
## When this runs
## The ZYNTH buyer frame
1. **Who signs / who champions** — the real decision-maker vs the influencer. In MM/SG SME brands this is often the MD/owner; in MNCs it's a Marketing/Brand Manager with a procurement gate. Name both roles.
2. **What they want** — the business outcome, not the deliverable ("more qualified walk-ins for the launch", not "a video").
3. **What they've tried** — previous agencies, in-house attempts, freelancers — and why it disappointed. This is the wedge.
4. **What's driving the decision now** — the trigger event (launch, rebrand, new fiscal budget, competitor move, expansion into MM or SG).
5. **Budget signal** — are they already spending (ads running, events done, sponsorships)? Visible spend > stated intent.
6. **Fear / risk they carry** — wasted budget, looking bad to their boss, launch slipping. Objections live here (hand to `zb-objections`).
## Fit score (routes the pipeline)
## Required output → BD lead DB fields
## Guardrails

## zb-objections
# zb-objections — ZYNTH Objection Handling
## Method
## The ZYNTH objection library
## Output
## Guardrails

## zb-offer
# zb-offer — ZYNTH Offer Construction
## The ZYNTH offer stack
1. **Core outcome** — the business result the buyer named in `zb-icp`, restated as the promise. (Not "6 reels" → "a launch month that fills the room and gets shared.")
2. **The mechanism** — *why ZYNTH's way works and the last agency's didn't.* This is our differentiation: bilingual MM/SG, event + video under one roof, intelligence-led creative. One sentence, specific.
3. **Deliverable stack** — what they actually receive, itemised, tied to a service tier so it's costable.
4. **Value amplifiers** — bonuses that cost us little and signal a lot (e.g. a post-campaign performance readout, a reusable brand asset, priority slot). Never discount the core; add to it.
5. **Risk reversal** — a milestone/gated structure or a clear revision policy, not money-back. Reduces the "new agency" fear surfaced in `zb-objections`.
6. **Price anchor + framing** — present the mid tier against a higher tier so the recommendation looks like the sensible choice. Anchor high, recommend middle.
7. **Reason to move now** — the real trigger (launch date, fiscal window, slot availability) — never fake scarcity.
## Costing law (non-negotiable)
## Currency + market
## Output
## Guardrails

## zb-pitch-kit
# zb-pitch-kit — ZYNTH Sales Enablement
## What the kit contains
1. **Pitch deck** — the proposal in presentation form, following the 11-section standard.
2. **One-pager** — the offer sheet compressed to a single leave-behind (outcome → mechanism → tiers → move-now).
3. **Objection pre-empt** — the "You might be wondering…" block from `zb-objections`.
4. **Demo / walkthrough script** — how Zane talks through the deck live, section by section, with the transitions and the ask.
## Mapping to the 11-section Proposal Standard
## Build sequence
## Output
## Guardrails

## zynth-3d-design-studio
# ZYNTH 3D & Design Studio
## The workflow (every asset)
1. **Direction** — the brief, the ONE idea, the exact style/technique and reference
2. **Generate** — the right tool for the job:
3. **Refine** — `upscale_image` (2K/4K), `remove_background` (cutouts), `outpaint_image`
4. **Apply & deliver** — put the asset into the format it's for (feed 1080×1350,
## Styles & techniques (produce across all)
## Running real generation (only in a live session)
## Standards
## Output

## zynth-3d-production
# ZYNTH 3D Production & Spatial Design Skill
## How to Use This Skill
## Skill Pillars
### 1. Exhibition Booth Design
### 2. Stage & AV Production
### 3. Blender Python Automation
## Reference Files
## ZYNTH guardrails (added on adoption — these override anything above)

## zynth-account-manager
# ZYNTH Account Manager
## Account Manager Responsibilities at ZYNTH
## 1. Proposal / Scope of Work (SOW)
### Proposal Structure:
## 2. Client Presentation Structure
### For strategy or campaign presentations:
### Presentation delivery notes:
## 3. Meeting Notes Template
## 4. Weekly Status Report
## 5. Market Research & Competitor Analysis
### Competitor Analysis Framework:
### Synthesis output:
### Research sources to use (Singapore & Myanmar):
## 6. Vendor & Third-Party Supplier Research
### Vendor Research Brief:
### Vendor Evaluation Table:
### Categories ZYNTH commonly sources:
## 7. Upsell Planning
### Upsell Triggers:
### Upsell Conversation Structure:
1. **Start with results:** What has ZYNTH delivered? Remind them of the value.
2. **Identify the gap:** What's the next problem or opportunity they have?
3. **Make the connection:** How does the proposed addition solve that?
4. **Quantify the opportunity:** What could they gain? (leads, reach, revenue)
5. **Make the ask:** Specific proposal, not a vague "we could also do..."
## 8. New Client Onboarding Checklist
## 9. Handling Difficult Client Situations
### Scope creep:
### Missed deadline (ZYNTH's fault):
### Unhappy client:
### Budget dispute:

## zynth-analytics-specialist
# ZYNTH Analytics Specialist
## Analytics Service Areas
## 1. Tracking Setup Checklist
### Google Analytics 4 (GA4):
### Meta Pixel:
### TikTok Pixel:
### Google Tag Manager (GTM) — recommended for all clients:
### UTM Naming Convention (ZYNTH standard):
## 2. Campaign Report Structure
### ZYNTH Campaign Report Template:
## 3. Monthly Performance Dashboard
### Metrics to include in every monthly dashboard:
## 4. Data Interpretation Framework
### Step 1 — What happened?
### Step 2 — Is this good or bad?
### Step 3 — Why did it happen?
### Step 4 — What should we do?
## 5. Attribution Guide
### Why numbers differ across platforms:
## 6. Reporting Quality Standards

## zynth-art-director
# ZYNTH Art Director
## Art Director Responsibilities at ZYNTH
## 1. Visual Brief
### Visual Brief Template:
## 2. Visual Identity System
### 2.1 Logo Direction
### 2.2 Colour System
### 2.3 Typography System
### 2.4 Imagery Style
### 2.5 Layout & Grid Principles
## 3. Social Media Visual Style Guide
### Template per platform:
## 4. Photography & Video Production Brief
## 5. Design Feedback Framework
### What good design feedback looks like:
### Design Review Questions:
1. **Does it express the idea?** Can you trace a line from the creative concept to this design?
2. **Is the hierarchy clear?** Does the eye know where to go first, second, third?
3. **Is it distinctive?** Could this design belong to any brand, or only this one?
4. **Does it work at all sizes?** Check: tiny (app icon) → medium (social) → large (billboard)
5. **Is it culturally appropriate?** For Singapore / Myanmar audience and context?
6. **Is it production-ready?** Correct specs, fonts embedded, assets at correct resolution?
## 6. Visual QC Checklist Before Client Submission

## zynth-bd-pitch-prep
# ZYNTH BD Pitch Prep
## What This Skill Produces
1. **Outreach Message** — personalised first contact (email / LinkedIn / Messenger / WhatsApp)
2. **Follow-up Sequence** — 2–3 follow-ups if no reply
3. **First Meeting Agenda** — structured 45–60 min discovery meeting
4. **Post-Meeting Summary Template** — to send after the meeting
## How to Use This Skill
## 1. Outreach Message
### The ZYNTH Outreach Formula:
1. **Proof you looked** — one specific, genuine observation about their business
2. **The gap** — what you noticed that could be better (frame as opportunity, not criticism)
3. **The hook** — one line on what ZYNTH does and why it's relevant to them specifically
4. **The ask** — one low-friction next step (not "buy from us" — "would you be open to a quick call?")
### Channel-Specific Versions:
### Personalisation Variables (fill from BD Research):
## 2. Follow-Up Sequence
## 3. First Meeting Agenda
## 4. Post-Meeting Follow-Up Email
## 5. Outreach Quality Checklist
## Banned Phrases in ZYNTH Outreach

## zynth-bd-researcher
# ZYNTH BD Researcher
## How to Use This Skill
## BD Intel Report Structure
### Section 1 — Company Snapshot
### Section 2 — Digital Presence Audit
### Section 3 — Content & Brand Assessment
### Section 4 — Competitor Landscape
### Section 5 — Growth Signals
### Section 6 — Pain Point Hypothesis
### Section 7 — ZYNTH Fit Score
### Section 8 — Recommended ZYNTH Services
### Section 9 — Outreach Intelligence
### Section 10 — Recommended Next Action
## Quick Research Mode
1. **Who they are:** [1 sentence]
2. **Digital health:** [1–10 score + biggest gap]
3. **Growth signal:** [Weak/Moderate/Strong]
4. **Best ZYNTH service fit:** [Top 1–2 services]
5. **Verdict:** [Hot / Warm / Cool / Pass + one reason]

## zynth-brand-strategist
# ZYNTH Brand Strategist
## Core Deliverables & When to Use Them
## 1. Brand Foundation (Primary Output)
### 1.1 Client Discovery Questions
### 1.2 Brand Positioning Statement
### 1.3 Brand Essence
### 1.4 Brand Values
### 1.5 Target Audience Profiles
### 1.6 Tone of Voice
### 1.7 Brand Story (Origin Narrative)
## 2. Brand Audit Framework
1. **Clarity** — Is the positioning instantly understood?
2. **Consistency** — Does the brand look and sound the same everywhere?
3. **Differentiation** — Is there a real, defensible difference from competitors?
4. **Relevance** — Does it resonate with today's audience in SG/Myanmar?
5. **Emotional resonance** — Does it make people feel something?
## 3. Competitive Positioning Map
## 4. Market-Specific Guidance
### Singapore
### Myanmar
## 5. Output Format Standards
## 6. Quality Checks Before Delivering

## zynth-campaign-planner
# ZYNTH Campaign Planner
## Campaign Types at ZYNTH
## 1. Campaign Brief (Core Output)
### Section 1 — Business Context
### Section 2 — Campaign Objective
### Section 3 — Target Audience
### Section 4 — Campaign Message
### Section 5 — Channel Plan
### Section 6 — Timeline
1. **Pre-launch / Teaser** (if applicable): Duration + activity
2. **Launch / Hero moment**: Duration + activity
3. **Sustain / Always-on**: Duration + activity
4. **Wind-down / Retargeting**: Duration + activity
### Section 7 — Budget Allocation
### Section 8 — KPIs & Measurement
## 2. Go-to-Market Launch Plan
### Pre-Launch Checklist
### Launch Week Plan
### Post-Launch Review (2–4 weeks in)
## 3. Channel Selection Guide by Market
### Singapore
### Myanmar
## 4. Campaign Sizing Guide
## 5. Output Format Standards
## 6. Quality Checks

## zynth-campaign-requirements
# ZYNTH Campaign Requirements Checklist
## How This Skill Differs from Project Manager
## Step 1 — Identify Campaign Type
1. **Campaign type** — which category applies?
2. **Market** — Singapore / Myanmar / Both
3. **Campaign duration** — one-off or ongoing retainer?
4. **Channels** — which platforms will this campaign run on?
## Master Requirements Checklist
### SECTION A — Brand & Creative Assets (All Campaigns)
### SECTION B — Client Information & Approvals
### SECTION C — Platform Access & Technical Setup
### SECTION D — Channel-Specific Requirements
#### D1 — Organic Social Media Campaign
#### D2 — Paid Advertising Campaign (Meta / Google)
#### D3 — Video Production
#### D4 — Event or Activation
#### D5 — Email Marketing
### SECTION E — Budget & Commercial
### SECTION F — Legal & Compliance
## Requirements Gap Report
## Quality Checks

## zynth-commercial-video-studio
# ZYNTH Commercial Video Studio — Pre to Post
## The pipeline (every job runs this)
1. **Brief & concept** — the objective, audience, one idea, the reference style/technique
2. **Script** — EN + Myanmar (Unicode/Pyidaungsu); hook in the first 3 seconds.
3. **Storyboard** — shot-by-shot. **Generate real frames** when useful:
4. **Shot list & plan** — camera, lens, movement, lighting, duration per shot; decide
5. **Real shoot** → produce the shoot brief + shot list for the crew
6. **AI-generated footage** → `Higgsfield.generate_video` (choose the model via
7. **Edit** — assembly to the script/story; pacing to the platform.
8. **Colour grade** — the look (Resolve node craft: NR → primaries → CST → look → polish;
9. **Sound** — VO / music / SFX (`Higgsfield.generate_audio` for score/VO when needed);
10. **Motion / VFX / titles** — kinetic type (EN + Burmese), lower-thirds, logo sting.
11. **Deliverables & export** — per platform: Reels/TikTok 1080×1920, feed 1080×1350,
## Styles & techniques (produce across all of them)
## Running real generation (only in a live session)
## Standards
## Output

## zynth-competitor-analyst
# ZYNTH Competitor Analyst
## How This Skill Differs from Market Researcher
## Deliverables & When to Use Them
## 1. Competitor Positioning Audit
### 1.1 Brand Identity
### 1.2 Target Audience
### 1.3 Messaging Architecture
### 1.4 Visual & Creative Identity
### 1.5 Channel Presence
### 1.6 Pricing Position
### 1.7 Strengths & Vulnerabilities
## 2. Competitor Content & Channel Audit
### Content Audit Framework
## 3. Competitor Perception Map
### Axes Selection
### Perception Map Output
## 4. Competitor Pricing Intelligence
## 5. Competitor Watch Brief (Monthly)
### What to Monitor
### Format
1. **What changed this month** — factual summary
2. **What it might mean** — strategic interpretation
3. **Recommended response** — should the client do anything in response?
## 6. Competitive Intelligence Sources
### Singapore
### Myanmar
### Universal Tools
## 7. Handling Incomplete Data
## 8. Output Standards
### "Where to Attack" Format
## 9. Quality Checks

## zynth-content-strategist
# ZYNTH Content Strategist
## What a Content Strategist Does at ZYNTH
## 1. Content Pillar Framework
### How to define pillars:
### Recommended pillar mix:
## 2. Platform Strategy
### Platform Roles at ZYNTH:
### Myanmar-specific platform note:
## 3. Content Calendar
### Monthly Content Calendar Structure:
#### Weekly Grid:
#### Monthly content mix target:
### Singapore Content Calendar Hooks:
### Myanmar Content Calendar Hooks:
## 4. Content Audit Framework
## 5. Content Brief (for Copywriter handoff)
## 6. Launch Content Plan
### 3-Phase Launch Content Structure:
## 7. Quality Checks

## zynth-copywriter
# ZYNTH Copywriter
## ZYNTH Copy Principles
1. **Lead with the idea, not the information.** Don't describe — provoke.
2. **Specificity over generality.** "Cuts onboarding time by 40%" beats "saves you time."
3. **One message per piece.** If it says three things, it says nothing.
4. **Earn the CTA.** The call-to-action should feel inevitable, not bolted on.
5. **Read it aloud.** If it sounds like a brochure, rewrite it.
## Format Playbooks
### 1. Social Media Copy
#### Structure per post:
#### Platform tone calibration:
#### Myanmar-specific note:
### 2. Video Scripts
#### Script structure (any length):
1. **Hook (0–3 sec):** Visual + verbal hook simultaneously. What makes someone NOT skip?
2. **Problem / Tension (3–10 sec):** Establish what's at stake. Create a question in the viewer's mind.
3. **Solution / Reveal (10–30 sec):** Introduce the brand/product/idea as the answer.
4. **Proof (30–45 sec):** One specific, believable reason to trust this.
5. **CTA (final 5 sec):** One action. One URL/handle/message.
#### Script format:
#### Script lengths:
#### Tips:
### 3. Ad Copy (Paid Campaigns)
#### For every ad, write 3 variations:
#### Ad anatomy:
#### Always provide copy in this table format:
### 4. Website Copy
#### Page-by-page approach:
### 5. Press Releases
#### Structure:
1. **Headline:** News-forward. What happened? Write it like a journalist would.
2. **Dateline:** City, Date —
3. **Lead paragraph:** Who, what, when, where, why — in 2–3 sentences. Most important fact first.
4. **Quote (spokesperson):** One quote from a senior figure. Should add perspective, not repeat the lead. Sounds like a human said it.
5. **Body paragraphs:** Supporting detail, context, background. Inverted pyramid — most important first.
6. **Boilerplate:** Standard "About [Company]" paragraph. 3–5 sentences.
7. **Media contact:** Name, email, phone.
8. **END notation:** Close with ### or -END-
#### Tone: Formal but not stiff. Factual but not dry. Every sentence should answer "why does this matter?"
### 6. Event Scripts & Agendas
#### Event Agenda format:
#### MC / Host Script structure:
#### Script writing rules for events:
## Copy Review Checklist
## Banned Words & Phrases at ZYNTH

## zynth-creative-director
# ZYNTH Creative Director
## What a Creative Director Does at ZYNTH
## 1. The Creative Brief
### ZYNTH Creative Brief Structure:
## 2. Creative Territories
### Territory Structure:
## 3. The Big Idea
### Big Idea Format:
## 4. Creative Feedback Framework
### The 5 Creative Review Questions:
1. **Is the idea there?**
2. **Is it true to the brief?**
3. **Is it distinctive?**
4. **Does the craft match the idea?**
5. **Is it ready for the client?**
### Feedback format:
## 5. Mood & Direction Notes
### Structure:
## 6. Creative Standards at ZYNTH
### What makes work ZYNTH-quality:
### What gets sent back:
### Questions to ask before presenting to a client:

## zynth-creative-video-director
# ZYNTH Creative Video Director
1. **Conceive** — invent the idea, the story, the world, the shots. Commercial-grade creative that is distinctive, strategically rooted, and producible on a Myanmar/Singapore budget.
2. **Craft** — execute (or give frame-accurate, tool-accurate instructions to execute) the edit, effects, colour, motion, VFX, and sound in DaVinci Resolve, Premiere Pro, and CapCut.
## How to use this skill (progressive disclosure)
## The pipeline you own
### 1 — Pre-production (where the film is really made)
### 2 — Production (protect the edit)
### 3 — Post-production (the craft layers, in order)
1. **Assembly / paper edit** → story first, no polish.
2. **Rough cut** → timing, pacing, structure locked.
3. **Fine cut / picture lock** → frame-accurate; client-approved before any finishing.
4. **Sound** → dialogue clean-up, SFX, music, mix (see sound reference).
5. **Motion graphics / titles / VFX** → only after picture lock.
6. **Colour grade** → correction first, then look (see colour reference).
7. **Finishing & export** → masters + platform versions + subtitles (see delivery specs).
## Generating storyboards & concept frames (you can actually draw)
## Commercial-level bar (don't ship below this)
## Working with other ZYNTH skills

## zynth-event-manager
# ZYNTH Event Manager
## ZYNTH Event Service Tiers (use for quoting)
## 1. Event Brief Intake (always start here)
## 2. Master Event Workplan (build backwards from event day)
## 3. Event Budget Template
1. **Venue** — rental, setup/teardown hours, insurance, permits
2. **F&B** — per-pax catering, beverages, service staff
3. **AV & Technical** — sound, lighting, LED/projection, livestream
4. **Production & Fabrication** — stage, backdrop, booths, signage, print
5. **Programme** — emcee, speakers, performers, entertainment
6. **Marketing & Content** — design, paid ads, photographer, videographer
7. **Logistics & Manpower** — transport, ushers, security, registration crew
8. **Guest Experience** — door gifts, lanyards, F&B vouchers, swag
9. **Contingency** — always 10% of subtotal
10. **ZYNTH Management Fee** — per tier table above
## 4. Run of Show (ROS) Format
## 5. Event Marketing Layer (ZYNTH's edge)
## 6. Risk & Contingency Checklist
## 7. Post-Event Report (client deliverable)
## Working with other ZYNTH skills

## zynth-market-researcher
# ZYNTH Market Researcher
## Research Deliverables & When to Use Them
## 1. Category Overview
### Structure:
## 2. Competitor Snapshot
## 3. Audience Insight Report
### 3.1 Audience Segmentation
### 3.2 Audience Tensions
### 3.3 The One Insight
## 4. Trend & Cultural Moment Scan
### Categories to scan:
1. **Macro trends** — Economic, social, or behavioural shifts affecting the market
2. **Category trends** — What's changing specifically in this industry
3. **Platform / media trends** — How content consumption is shifting (relevant to Singapore / Myanmar)
4. **Cultural moments** — Upcoming festivals, national events, tentpole occasions
### Singapore Cultural Calendar (Key Moments)
### Myanmar Cultural Calendar (Key Moments)
## 5. Market Opportunity Brief
1. **The Opportunity** — What gap exists and why now?
2. **The Audience** — Who is ready to buy, and what do they currently lack?
3. **The Competition** — Who occupies adjacent space, and why are they vulnerable?
4. **The Entry Point** — What is the most credible, low-risk way to enter?
5. **The Risk** — What could go wrong, and how do we mitigate it?
6. **The Ask** — What does ZYNTH recommend the client do next?
## 6. Research Quality Standards
### Source Hierarchy (use in order of reliability)
### How to Handle Data Gaps
## 7. Output Format Standards
## 8. Quality Checks

## zynth-master-campaign-planner
# ZYNTH Master Campaign Planner
## Non-negotiable standards
1. **Complete or nothing.** Produce every section in `references/output-contract.md`.
2. **Sector-grounded.** Open `references/sectors.md` for the client's industry and
3. **Real market money.** Price with `references/commercial-model.md` — real MMK/SGD
4. **Creative direction, not just tactics.** Every plan states the big idea, the
5. **Show the value.** Make the client's benefit and ROI explicit and quantified —
6. **Honest commercial model.** Decide and justify: does the client fund this
## How to run a plan (the process)
1. **Capture the brief** — client, sector, objective, budget band, market (MM/SG),
2. **Load the sector pack** (`references/sectors.md`) and the market rates
3. **Run the method** (`references/method.md`) — the ZYNTH frameworks that turn a
4. **Assemble to the full output contract** (`references/output-contract.md`).
5. **Self-check against the Critic rubric** at the end of the output contract:
## Financial law (every plan)
## References (read the ones the task needs)

## zynth-master-event-planner
# ZYNTH Master Event Planner
## Non-negotiable standards
1. **Complete or nothing.** Produce every section in `references/output-contract.md`.
2. **Sector-grounded.** For the client's industry, read the sector packs in the
3. **Real market money.** Price with `references/production-costs.md` — real MMK/SGD
4. **Produceable, not just pretty.** Every creative idea maps to a real production
5. **Operations that hold on the day.** A real run-of-show, crew roles, SOPs, and a
6. **Show the value + honest funding model.** Make the client's result explicit, and
## How to run an event plan (the process)
1. **Capture the brief** — client, sector, objective, guest count & profile, market
2. **Load the references** — `references/production-costs.md` (rates), the sector
3. **Run the method** (`references/method.md`) — concept → experience journey →
4. **Assemble to the full output contract** (`references/output-contract.md`).
5. **Self-check against the Critic rubric** at the end of the output contract. Fix
## Financial law (every plan)
## References (read the ones the task needs)

## zynth-master-proposal-writer
# ZYNTH Master Proposal Writer
## The winning standard (non-negotiable)
1. **Client-first, not ZYNTH-first.** Open with THEIR problem and world, in their words.
2. **One sharp idea, made vivid.** A distinctive, defensible big idea — expressed so the
3. **Complete & systematic.** Every section of `references/output-contract.md`, fully
4. **Accurate & real-money.** Priced at real MMK/SGD market rates, market FX
5. **Value made unmistakable.** The result and ROI stated as a single number the client
6. **Proof.** Credibility woven in — relevant thinking, method, and "Why ZYNTH" (speed,
7. **Winning close.** Clear commercial model (sell vs sponsor), terms, and a single,
## How to write a winning proposal (the process)
1. **Capture the brief** — client, sector, objective, budget band, market (MM/SG),
2. **Get the strategy** — if there isn't already a plan, run
3. **Load the sector pack** (`../zynth-master-campaign-planner/references/sectors.md`) so
4. **Read the winning playbook** (`references/winning-playbook.md`) — what makes proposals
5. **Assemble to the output contract** (`references/output-contract.md`).
6. **Run the discussion + Critic pass** — put the draft through the ZYNTH roundtable
## Financial law (every proposal)
## References

## zynth-paid-media-specialist
# ZYNTH Paid Media Specialist
## Platform Coverage
## 1. Media Plan
### Media Plan Structure:
#### Budget Allocation Table:
#### Platform Rationale:
#### Recommended Timeline:
## 2. Meta Ads (Facebook & Instagram)
### Campaign Structure (always use this hierarchy):
### Objective Selection Guide:
### Audience Setup:
### Ad Formats & When to Use:
### Meta Benchmarks (Singapore market):
### Myanmar Meta Notes:
## 3. TikTok Ads
### Campaign Structure:
### Objective Selection:
### Audience Targeting on TikTok:
### Creative Requirements for TikTok Ads:
### TikTok Benchmarks (Singapore):
## 4. Google Ads
### Search Campaign Setup:
### Google Display — Retargeting Setup:
## 5. A/B Testing Framework
## 6. Optimisation Checklist (Weekly)
## 7. Reporting Metrics by Objective

## zynth-pitch-packager
# ZYNTH Pitch & Proposal Packager
## How This Skill Differs from Account Manager
## Pitch Pack Types
## 1. New Business Pitch Structure
### Slide / Section 1 — The Opening Statement
### Slide / Section 2 — The Problem We're Solving
### Slide / Section 3 — The Market Landscape
### Slide / Section 4 — Our Recommended Approach
### Slide / Section 5 — What We'll Do (Scope)
### Slide / Section 6 — The Creative Idea (if applicable)
### Slide / Section 7 — The Media Plan (if applicable)
### Slide / Section 8 — The Numbers
### Slide / Section 9 — Why ZYNTH
1. **Relevant experience:** One example most relevant to this client's category or challenge
2. **What makes ZYNTH different:** One distinctive thing about how ZYNTH works
3. **The team:** Who will work on this account (names, roles, one-line background)
### Slide / Section 10 — Next Steps
## 2. Campaign Proposal Structure
## 3. One-Pager Format
## 4. Campaign Wrap-up + Upsell Pack
## 5. Pitch Writing Principles
### Lead with the client, not with ZYNTH
### One idea per slide / section
### Write headlines that carry the argument
### Make the numbers feel safe
### End with momentum
## 6. Assembling from Other Agents — Input Checklist
## 7. Tone & Language Standards
## 8. Quality Checks

## zynth-project-manager
# ZYNTH Project Manager
## Project Types at ZYNTH
## 1. Project Kickoff Checklist
## 2. Project Timeline Template
## 3. ZYNTH File & Folder Naming Convention
### Folder structure per client:
### File naming convention:
## 4. Content Production Workflow (Retainer)
## 5. Task Brief Template
## 6. Campaign Project Checklist
## 7. Recommended PM Tools for ZYNTH
### If starting from scratch (recommended for ZYNTH now):
### For task and deadline management:
### For file storage:
### For client communication:
### Minimum viable setup for ZYNTH today:
## 8. Managing Deadlines & Escalation
### When a deadline is at risk:
### Escalation triggers (flag to leadership):
### Change order trigger:

## zynth-seo-specialist
# ZYNTH SEO Specialist
## SEO Service Areas
## 1. Keyword Research Framework
### Step 1 — Seed Keywords
### Step 2 — Keyword Classification
### Step 3 — Keyword Prioritisation Matrix
### Step 4 — Keyword Mapping
## 2. On-Page SEO Checklist
### Title Tag:
### Meta Description:
### Header Tags:
### Body Content:
### Images:
### URL Structure:
## 3. Technical SEO Audit Checklist
### Crawlability & Indexing:
### Site Speed (Core Web Vitals):
### Mobile:
### HTTPS & Security:
### Structured Data (Schema):
## 4. Local SEO (Singapore Focus)
### Google Business Profile (GBP) Optimisation:
### Review Strategy:
### Local Citations:
## 5. SEO Content Brief
## 6. SEO Reporting
### Monthly SEO Report Structure:
1. **Rankings Summary** — Position changes for top 20 target keywords
2. **Organic Traffic** — Sessions, users, trend vs. last month and YoY
3. **Top Landing Pages** — Which pages are driving the most organic traffic
4. **Technical Health** — Any new crawl errors, Core Web Vitals changes
5. **Wins This Month** — Pages that improved, new keywords ranking
6. **Issues to Address** — Priority technical or content fixes
7. **Next Month Focus** — Top 3 priorities
### Core SEO Metrics to Track:

## zynth-social-media-manager
# ZYNTH Social Media Manager
## Platform Management Guide
### Instagram
### Facebook
### TikTok
### LinkedIn (for B2B clients)
## Community Management Framework
### Response Time Standards:
### Response Tone Guide:
### Crisis Response Protocol:
## Influencer Management
### Influencer Tier Guide (Singapore):
### Influencer Brief Checklist:
### Influencer Vetting Checklist:
## Monthly Social Media Report Structure
### Report sections:
1. **Executive Summary** — 3 bullet points: what worked, what didn't, what's next
2. **Platform Performance Overview** — key metrics vs. previous month and targets
3. **Top Performing Content** — top 3 posts per platform with learnings
4. **Community Growth** — follower count, growth rate, DM volume
5. **Engagement Analysis** — engagement rate trend, comment sentiment
6. **Recommendations** — 3 specific changes for next month based on data
### Core metrics to track per platform:
## Social Media Audit Framework

## zynth-sponsorship-value
# ZYNTH Agency: Sponsorship & Value Proposition Skill
## 1. Capabilities:
## 2. AI Integrations:
## 3. Specialized Methods & SOPs:
## ZYNTH guardrails (added on adoption — these override anything above)

## zynth-tactical-prompts
# ZYNTH Tactical Prompt Library
## How to Use This Skill
### Prompt Categories:
## Reference Prompts
## ZYNTH guardrails (added on adoption — these override anything above)

## zynth-vendor-finder
# ZYNTH Vendor Finder
## How to Use This Skill
1. **State the category** — What type of vendor are you looking for?
2. **State the market** — Singapore / Myanmar / Both
3. **State the budget range** — even a rough estimate helps narrow options
4. **State the timeline** — some vendors need 2 weeks notice; others need 2 months
5. **State the deliverable** — what exactly needs to be produced?
## Vendor Categories at ZYNTH
### Category 1 — Photography
### Category 2 — Video Production
### Category 3 — Printing & Production Materials
### Category 4 — Event Production & Management
### Category 5 — Influencer & Content Creators
### Category 6 — Digital & Tech Vendors
### Category 7 — Translation & Localisation
## Vendor Briefing Template
## Quality Checks Before Engaging Any Vendor

## zynth-video-producer
# ZYNTH Video Producer
## ZYNTH Video Service Tiers (use for quoting)
## 1. Video Brief Intake
## 2. Pre-Production Pack (ZYNTH's core deliverable)
1. **Concept** — one-paragraph idea + reference videos (route to **zynth-creative-director** for concept development)
2. **Script / VO** — route to **zynth-copywriter**; bilingual EN/MM where needed
3. **Storyboard or shot list** — see format below
4. **Production schedule** — call time, locations, scene order, wrap
5. **Talent & location plan** — releases signed, permits checked
6. **Production house brief** — see Section 4
## 3. Video Budget Template
## 4. Production House Briefing Template
## 5. Post-Production Workflow
## 6. Social-First Video Rules (priority work)
## Working with other ZYNTH skills
