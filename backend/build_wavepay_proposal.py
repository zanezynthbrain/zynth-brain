"""WAVE PAY PREMIUM LAUNCH — the ZYNTH proposal, built to the full standard.

Run from backend/:  python build_wavepay_proposal.py

Rebuilt from the July draft, with two things fixed and a lot added:

* Money. The draft priced ZYNTH at "18% of project cost" and printed a 15.3%
  margin — below the R1 floor and 54M MMK under-priced. Its own Production
  subtotal was also 2.5M out. Every figure here is summed by utils.proposal_doc
  and priced at the 40% target.
* Creative. The draft had a theme and a palette. A client buys the *reason* —
  the insight, why this idea and not the obvious one, and what a guest actually
  feels minute by minute. That is now the longest section in the document.

Outputs Markdown + .docx from one definition so they cannot drift.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.proposal_doc import costing_from_rows, commercial_model, review
from utils.proposal_render import render_both, money_table, budget_table

CLIENT = "WavePay Myanmar"
TITLE = "The Next Wave — WavePay Premium Launch"
SLUG = "2026-09_WavePay_TheNextWave_v1"

BUDGET_ROWS = [
    ("Venue & Hospitality", "Crystal Ballroom, LOTTE Hotel Yangon — 5 hours", 1, 15_000_000),
    ("Venue & Hospitality", "Hospitality staff (ushers, cloakroom)", 10, 100_000),
    ("Venue & Hospitality", "Cleaning & additional security", 1, 4_000_000),
    ("Production", "Main stage + LED tunnel + lounge build", 1, 20_000_000),
    ("Production", "Lighting — 12 movers, 16 washes, 4 profiles, 2 lasers", 1, 7_000_000),
    ("Production", "Sound — line array, monitors, wireless, console", 1, 4_000_000),
    ("Production", "LED — 10x4m main wall + tunnel screens", 1, 8_000_000),
    ("Production", "Video production — content, live feed, highlight reel", 1, 4_000_000),
    ("Production", "Special effects — haze, projection mapping, confetti", 1, 3_000_000),
    ("Production", "Technical crew (show day)", 8, 625_000),
    ("Talent", "Bilingual MC", 1, 2_000_000),
    ("Talent", "DJ — electronic-jazz fusion", 1, 1_000_000),
    ("Talent", "Futurist dance performance", 1, 2_500_000),
    ("Catering", "Premium canapés & beverages", 250, 50_000),
    ("Marketing", "Event photography + editing", 1, 1_500_000),
    ("Marketing", "Printing, signage, invitations, welcome kits", 1, 1_000_000),
    ("Marketing", "Fabrication — interactive touch-tables", 1, 2_500_000),
    ("Staffing", "ZYNTH on-site event management team", 5, 1_000_000),
    ("Transport", "VIP & talent transport", 1, 1_000_000),
]

costing = costing_from_rows(
    [{"category": c, "item": i, "qty": q, "unit_cost_mmk": u} for c, i, q, u in BUDGET_ROWS]
)
CM = commercial_model(costing)
PRICE = CM["client_price_mmk"]


SECTIONS = [
 {"heading": "Executive Summary",
  "body": (
    "WavePay made digital payment ordinary in Myanmar. That is the achievement and, "
    "commercially, the problem: a utility is used, not chosen. WavePay Premium has to "
    "be chosen.\n\n"
    "This proposal is for a single evening on 17 September 2026 in the Crystal Ballroom "
    "at LOTTE Hotel Yangon, in front of 250 named guests — 30 VIPs and regulators, 40 "
    "media and KOLs, 50 strategic partners, and 130 pre-selected SME owners and young "
    "professionals who are the actual first cohort of Premium.\n\n"
    "The idea is \"The Next Wave\". Not a feature launch — a status launch. The evening "
    "is engineered so that a guest physically crosses from the ordinary into the premium "
    "and feels the difference before a single slide is shown.\n\n"
    f"Investment: {PRICE:,.0f} MMK (USD {CM['client_price_usd']:,.0f}), turnkey — creative, "
    "production, vendor management, marketing and execution. ZYNTH carries the vendor "
    "relationships, the risk register and the run of show; WavePay approves and shows up."),
  "tables": [{"title": "At a glance", "headers": ["", ""], "rows": [
      ["Event", "The Next Wave — WavePay Premium Launch"],
      ["Date", "Thursday 17 September 2026, 17:30–21:30"],
      ["Venue", "Crystal Ballroom, LOTTE Hotel Yangon"],
      ["Guests", "250, curated by segment"],
      ["Format", "Premium reception + keynote + reveal"],
      ["Investment", f"{PRICE:,.0f} MMK (USD {CM['client_price_usd']:,.0f})"],
      ["Deposit to secure", f"{CM['deposit_mmk']:,.0f} MMK (50%)"]]}]},

 {"heading": "Strategic Context — Why Now",
  "body": (
    "Three things make September the window, and they will not all be true again "
    "for a year.\n\n"
    "**The category is commoditising.** Every wallet in Myanmar now does transfer, "
    "top-up and bill pay. Competition has moved from capability to identity: not what "
    "the app does, but what carrying it says about you. Premium is the first product "
    "in the category that can be positioned on identity — but only if it is launched "
    "that way. Launched as a feature list, it becomes a settings screen.\n\n"
    "**The audience is mid-cycle.** Yangon SME owners and young professionals do their "
    "Q4 planning in September and October. Reaching them in September puts WavePay "
    "Premium inside a decision they are already making, rather than interrupting one "
    "they are not.\n\n"
    "**The calendar is clear.** September (Tawthalin) sits after Buddhist Lent and "
    "before Thadingyut. It is one of the few clean windows for a corporate premium "
    "launch that is neither competing with festival noise nor culturally inappropriate "
    "for a celebration.\n\n"
    "The risk of waiting is specific: a competitor announces a premium tier first and "
    "WavePay's launch becomes a response instead of a move."),
  "tables": []},

 {"heading": "Objectives & How We Will Know It Worked",
  "body": (
    "Four objectives, in priority order. Each has a number attached so the evening can "
    "be judged rather than admired."),
  "tables": [{"headers": ["Priority", "Objective", "Success measure"], "rows": [
      ["1", "Convert the room", "10% of attendees activate Premium within 24 hours"],
      ["2", "Own the category narrative", "10+ tier-one articles carrying the positioning, not just the news"],
      ["3", "Build the partner runway", "50 strategic partners in the room; 12 follow-up meetings booked on the night"],
      ["4", "Give sales a year of assets", "Highlight film, 300+ edited stills, 6 testimonial clips, full photo library"]]}]},

 {"heading": "Who Is In The Room",
  "body": (
    "Attendance is allocated against a target composition, not sold or opened. The list "
    "is the product: a room where every WavePay salesperson can find a buyer, and no "
    "guest meets only competitors.\n\n"
    "Invitations go out in three waves — VIP and media first (personal, physical), "
    "partners second, target users third — so that acceptance from the top of the room "
    "makes acceptance further down easier."),
  "tables": [{"headers": ["Segment", "Seats", "Who exactly", "Why they matter"], "rows": [
      ["VIPs & executives", "30", "WavePay C-suite, Yoma Bank executives, regulators", "Signals legitimacy; regulators seeing it first prevents friction later"],
      ["Media & KOLs", "40", "Tech/business journalists, finance and lifestyle creators", "Carry the narrative beyond the room"],
      ["Strategic partners", "50", "Key merchants, corporates, telco representatives", "Premium needs an acceptance network on day one"],
      ["Target users", "130", "Pre-selected SME owners, young professionals, HNWIs", "The actual first cohort — chosen, not walk-in"],
      ["Total", "250", "", ""]]}]},

 {"heading": "The Creative Concept",
  "body": (
    "### The insight\n\n"
    "Premium products in Myanmar are usually sold on *more* — more limits, more "
    "features, more perks. But the people we are targeting are not short of features. "
    "They are short of **certainty**. An SME owner moving 8 million kyat does not want "
    "a bigger limit; they want to stop refreshing the screen. A young professional does "
    "not want another cashback tier; they want to feel that their money is handled by "
    "something serious.\n\n"
    "Premium is not more. Premium is **calm**.\n\n"
    "### The idea\n\n"
    "**\"The Next Wave.\"** A wave is WavePay's own name and its own metaphor — but the "
    "draft used it decoratively. We use it structurally: the entire evening is built as "
    "one wave. Guests physically travel from turbulence into stillness, and the product "
    "is revealed at the exact moment the room becomes quiet.\n\n"
    "**EN:** \"Your money, finally still.\"\n"
    "**MM:** \"သင့်ငွေ — ငြိမ်သက်စွာ။\"\n\n"
    "*(The Burmese is written first and the English transcreated from it, not the "
    "reverse. All Burmese type is set by hand, never generated inside an image.)*\n\n"
    "### Why this idea and not the obvious one\n\n"
    "The obvious launch is a countdown, a logo animation and a CEO saying \"we are "
    "excited to announce\". Every fintech in the region has run it, and it says nothing "
    "a competitor could not say next month. Worse, it sells Premium on novelty — and "
    "novelty expires, taking the positioning with it.\n\n"
    "\"Calm\" is defensible because it is an experience claim, not a feature claim. A "
    "competitor can copy a limit overnight. They cannot copy the memory of the room "
    "going silent.\n\n"
    "### The narrative arc — the wave, in four movements\n\n"
    "**1. Turbulence (arrival, 17:30).** The LED tunnel is *not* a pretty light show. "
    "It runs dense, fast, overlapping data — transaction noise, notification pings, "
    "numbers moving too quickly to read. It is deliberately slightly too much. Guests "
    "walk 5 metres through the everyday condition of their financial lives.\n\n"
    "**2. Surface (lounge, 18:00).** The tunnel opens into the Premium Lounge and the "
    "noise drops by half. Warmer light, slower music, touch-tables where the app "
    "responds instantly. The contrast is the message; nobody has to explain it.\n\n"
    "**3. Stillness (the reveal, 18:45).** At the peak of the keynote the room does "
    "something no Yangon launch does: **everything stops**. Lights to near-black, "
    "music out, LED wall to a single held frame. Three full seconds of silence. Then "
    "one line of type resolves: *Your money, finally still.* The product appears in the "
    "quiet, not the noise.\n\n"
    "**4. Momentum (panel to close, 19:15–21:30).** Energy returns, but warm rather "
    "than frantic — real SME owners, real numbers, then networking with the acceptance "
    "network already in the room.\n\n"
    "### Visual identity\n\n"
    "Deep navy (#0B1F3A) as the ground — trust, and it makes gold and cyan read as "
    "precious rather than loud. Metallic gold (#B88A2A) reserved *only* for Premium "
    "moments, so the eye learns to associate it with the tier. Electric cyan (#00C2D1) "
    "for data and motion. Clean geometric sans in English; Pyidaungsu for Burmese, set "
    "at 1.4x line height so the two scripts sit comfortably together.\n\n"
    "Imagery is fluid dynamics — ink dispersing in water, shot slow — never stock "
    "\"businesspeople shaking hands\". Materials: brushed metal, dark acrylic, warm "
    "light on skin.\n\n"
    "### Tone\n\n"
    "Composed. Quietly expensive. Closer to a private bank than a tech keynote. No "
    "hype cuts, no countdown clock, no confetti until the very end. The energy comes "
    "from the build, not the speed."),
  "tables": [{"title": "The four movements, as production cues",
      "headers": ["Movement", "Time", "Light", "Sound", "What the guest feels"], "rows": [
      ["Turbulence", "17:30", "Cold cyan, high frequency", "Dense, layered, slightly too loud", "The everyday — noise"],
      ["Surface", "18:00", "Warm gold, low and wide", "Electronic-jazz, slow", "Relief, arrival"],
      ["Stillness", "18:45", "Near black → single frame", "Full silence, 3 seconds", "Attention. The product lands here"],
      ["Momentum", "19:15", "Warm, full, human", "Live, conversational", "Confidence, then connection"]]}]},

 {"heading": "Guest Journey — Minute by Minute",
  "body": (
    "Every touchpoint from car door to goodbye, with the person responsible. This is "
    "the section that separates an event that looks good in photos from one that feels "
    "right to attend."),
  "tables": [{"headers": ["Touchpoint", "What happens", "Owner"], "rows": [
      ["Arrival, 17:25", "Named greeter at the car door — no clipboard hunting", "Guest Services"],
      ["Registration", "Face-matched to pre-registered list; badge already printed", "Registration Lead"],
      ["The tunnel", "5m walk through the data storm; staff do not talk here", "Technical Director"],
      ["Lounge entry", "Drink offered within 15 seconds of exit", "F&B Captain"],
      ["Touch-tables", "Two product specialists per table, not salespeople", "WavePay Product"],
      ["Seating call", "Chimes, not announcements; VIPs walked, not directed", "Event Manager"],
      ["The silence", "All staff freeze — no service movement for 3 seconds", "Show Caller"],
      ["Post-reveal", "QR activation on every table; specialists circulate", "WavePay Product"],
      ["Departure", "Welcome kit handed, not stacked; car called ahead", "Guest Services"]]}]},

 {"heading": "Run of Show",
  "body": "Load-in, show and strike. Times are cue times, not intentions.",
  "tables": [
    {"title": "Load-in (show day)", "headers": ["Time", "Segment", "Owner"], "rows": [
      ["08:00–12:00", "Venue access; stage, LED, sound, lighting load-in", "Production Manager"],
      ["12:00–14:00", "Technical setup, sound check, lighting focus, LED sync", "Technical Director"],
      ["14:00–16:00", "Decor, floral, catering stations, lounge dress", "Event Manager"],
      ["16:00–17:00", "Full technical rehearsal — every cue, including the silence", "Production Team"],
      ["17:00–17:30", "Staff briefing, guest flow walk-through, final checks", "Event Manager"]]},
    {"title": "Show", "headers": ["Time", "Segment", "Owner"], "rows": [
      ["17:30–18:00", "Arrival, LED tunnel, registration, welcome drinks", "Registration Team"],
      ["18:00–18:30", "Premium Lounge — networking, touch-table demos", "MC"],
      ["18:30–18:45", "Opening remarks", "MC / WavePay executive"],
      ["18:45–19:15", "Keynote and the reveal (the silence at 19:02)", "WavePay CEO"],
      ["19:15–19:45", "Panel — SME growth and digital finance", "Moderator + 3 panelists"],
      ["19:45–20:15", "Live product demo and Q&A", "WavePay Product"],
      ["20:15–20:45", "Performance", "Choreographer"],
      ["20:45–21:15", "Networking and close; activation push", "MC"],
      ["21:15–21:30", "Departure, welcome kits", "Guest Services"]]},
    {"title": "Strike", "headers": ["Time", "Segment", "Owner"], "rows": [
      ["21:30–00:30", "Production strike and load-out", "Production Manager"],
      ["00:30–01:30", "Venue clean-up and handover", "Venue Staff"]]}]},

 {"heading": "Stage, Production & Technical Design",
  "body": (
    "**Main stage.** 10m W x 5m D x 1m H with a 3m central thrust. High-gloss black "
    "acrylic deck with integrated LED edge strips. Seamless 10m x 4m LED wall behind "
    "(P2.6 indoor — at 3m viewing distance P3.9 will show pixel structure on the "
    "held reveal frame, which is the one shot that must be flawless).\n\n"
    "**LED tunnel.** 5m long, 3m high, 2.5m wide, curved. Content is generative and "
    "reactive; the reactivity is the point — guests must sense the noise is *theirs*.\n\n"
    "**Premium Lounge.** Modular, four zones, brushed metal and dark acrylic, four "
    "interactive touch-tables, branded bar.\n\n"
    "**Lighting.** 12 moving-head spots for beams and aerials, 16 LED washes for "
    "colour states, 4 profiles for key light on speakers, 2 RGB laser units. Haze "
    "throughout — beams do not exist without it.\n\n"
    "**Sound.** Line array sized to the ballroom, 4–6 stage monitors, wireless "
    "handhelds plus lapels for presenters, digital console with a dedicated engineer. "
    "The silence cue is programmed as a hard mute, not a fade.\n\n"
    "**A 3D previsualisation of the stage, tunnel and lounge is produced in Blender "
    "before any fabrication is committed** — so WavePay approves the room from every "
    "angle rather than approving a drawing."),
  "tables": [{"title": "LED content plan", "headers": ["Moment", "Content"], "rows": [
      ["Pre-event", "Abstract fluid motion, branding, countdown"],
      ["Arrival", "Reactive data storm (tunnel)"],
      ["Opening", "Corporate film, animated identity"],
      ["Keynote", "Presentation, live camera feed"],
      ["The reveal", "Held single frame, then the line, then UI walkthrough"],
      ["Panel", "Lower-thirds, speaker profiles, live feed"],
      ["Networking", "Ambient fluid motion, moderated social wall"]]}]},

 {"heading": "Vendor Requirements",
  "body": (
    "Every category has a named primary, a named backup and a lead time. ZYNTH holds "
    "all vendor contracts and manages performance; WavePay has a single point of "
    "contact.\n\n"
    "**All costs below are ZYNTH's current Yangon rate card and are marked "
    "[UNVERIFIED — Jul 2026] pending one confirmed written quote per line.** They will "
    "be replaced with signed quotes before contract. We would rather be corrected on a "
    "real number than believed on an estimate."),
  "tables": [{"headers": ["Category", "Primary", "Est. cost (MMK)", "Lead time", "Backup"], "rows": [
      ["Stage & fabrication", "Myanmar Event Management Co.", "20,000,000", "4 weeks", "iD Creative Solutions"],
      ["Lighting", "Light & Sound Myanmar", "7,000,000", "3 weeks", "Pro Audio & Lighting"],
      ["Sound", "Pro Audio & Lighting", "4,000,000", "3 weeks", "Light & Sound Myanmar"],
      ["LED screens", "Myanmar LED Solutions", "8,000,000", "3 weeks", "Global LED Myanmar"],
      ["Video production", "Yangon Film Services", "4,000,000", "6 weeks", "Myanmar Motion Pictures"],
      ["Photography", "The Photo Studio Yangon", "1,500,000", "2 weeks", "Myanmar Photography Group"],
      ["MC", "Bilingual MC (to confirm)", "2,000,000", "4 weeks", "Second MC shortlisted"],
      ["Music", "DJ (to confirm)", "1,000,000", "3 weeks", "Second DJ shortlisted"],
      ["Catering", "LOTTE Hotel (in-house)", "12,500,000", "6 weeks", "Chatrium Hotel"],
      ["Decor & floral", "Floral Art Myanmar", "2,500,000", "3 weeks", "Yangon Flower Shop"],
      ["Print & signage", "Print Master Myanmar", "1,000,000", "2 weeks", "Express Print Yangon"],
      ["Interactive builds", "Custom Props Myanmar", "2,500,000", "4 weeks", "Event Decor & Props"],
      ["Security", "Venue in-house", "included", "2 weeks", "Private security"],
      ["Transport", "Yangon Limousine", "1,000,000", "2 weeks", "Grab Business"]]}]},

 {"heading": "Marketing & Promotion",
  "body": (
    "Six weeks before, the night itself, and two weeks after. The campaign sells the "
    "*idea*, not the invitation — so that the 24 million people not in the room still "
    "receive the positioning."),
  "tables": [
    {"title": "Pre-event", "headers": ["Week", "Phase", "Deliverables"], "rows": [
      ["1–2", "Strategy & assets", "Messaging, identity guidelines, press kit, content calendar"],
      ["3", "Teaser", "Cryptic social teasers, 15s film, physical VIP invitations"],
      ["4", "Announcement", "Press release, landing page, targeted digital"],
      ["5–6", "Engagement", "Executive interviews, KOL partnerships, reminders"]]},
    {"title": "On the night", "headers": ["Activity", "Detail"], "rows": [
      ["Live coverage", "Real-time stories across WavePay and partner channels"],
      ["Media desk", "Check-in, press kits, interview scheduling"],
      ["Capture", "Photography, video, 6 testimonial interviews"],
      ["Activation", "QR on every table, moderated social wall"]]},
    {"title": "Post-event", "headers": ["Week", "Deliverables"], "rows": [
      ["1", "Highlight film (2–3 min), photo gallery, post-event release"],
      ["2", "Thank-you sequence, media coverage report, analytics report"]]}]},

 {"heading": "Content & Asset Deliverables",
  "body": "What WavePay owns after the night — the reason the investment outlives the evening.",
  "tables": [{"headers": ["Asset", "Spec", "Delivery"], "rows": [
      ["Teaser film", "15s, 9:16 + 1:1 + 16:9, bilingual subtitles", "2 weeks pre-event"],
      ["Corporate film", "90s, 16:9 4K", "1 week pre-event"],
      ["Highlight film", "2–3 min, 16:9 + 9:16 cutdown", "7 days post"],
      ["Testimonial clips", "6 x 30–45s, subtitled", "10 days post"],
      ["Photography", "300+ edited stills, full rights", "5 days post"],
      ["3D previsualisation", "Stage, tunnel, lounge — all angles", "Week 2"],
      ["Social cutdowns", "12 assets sized per platform", "14 days post"]]}]},

 {"heading": "Budget",
  "body": (
    "Every line is quantity x unit cost, summed. No line is a range: a range is an "
    "estimate, and an estimate is not a budget.\n\n"
    "Cost bands are [UNVERIFIED — Jul 2026] until each is replaced by a written quote."),
  "tables": [budget_table(costing)]},

 {"heading": "Commercial Model",
  "body": (
    "ZYNTH quotes a single turnkey investment, not a cost-plus-fee. The reason is "
    "practical: a percentage fee rewards us for spending more of your money, and a "
    "turnkey price does not.\n\n"
    f"**Investment: {PRICE:,.0f} MMK (USD {CM['client_price_usd']:,.0f}).** This covers "
    "creative direction, production management, all vendor contracts and payments, "
    "marketing execution, on-site delivery and post-event reporting.\n\n"
    f"{CM['payment_terms']}\n\n"
    "Contingency is held by ZYNTH and reconciled after the event: unspent contingency "
    "is returned, not retained. Scope changes are quoted in writing before work begins."),
  "tables": [money_table(CM)]},

 {"heading": "Timeline",
  "body": "Ten weeks from signature to final report. Week 1 begins on receipt of deposit.",
  "tables": [{"headers": ["Week", "Phase", "Key deliverable"], "rows": [
      ["1", "Kick-off & planning", "Project plan, venue contracted, creative brief"],
      ["2", "Creative & design", "Concept presentation, 3D stage previsualisation"],
      ["3", "Content & technical", "Run of show, scripts, technical rider"],
      ["4", "Marketing & guests", "Campaign live, guest list locked, invitations out"],
      ["5", "Production", "Fabrication begins; catering and talent contracted"],
      ["6", "Content production", "All films and decks complete; rehearsals scheduled"],
      ["7", "Logistics", "Transport, staffing roster, preliminary AV tests"],
      ["8", "Execution", "Load-in, rehearsal, the event"],
      ["9", "Reconciliation", "Strike, financial reconciliation, media monitoring"],
      ["10", "Final delivery", "Highlight film, gallery, full report, debrief"]]}]},

 {"heading": "Team & Responsibilities",
  "body": "Who does what, so nothing sits in the gap between two people.",
  "tables": [{"headers": ["Role", "Responsible for", "Side"], "rows": [
      ["ZYNTH Project Lead", "Single point of contact, commercials, escalation", "ZYNTH"],
      ["Creative Director", "Concept, identity, content direction", "ZYNTH"],
      ["Production Manager", "Build, vendors, load-in/strike, site safety", "ZYNTH"],
      ["Technical Director", "AV, LED, show cues, rehearsal", "ZYNTH"],
      ["Event Manager", "Guest flow, staffing, run of show on the night", "ZYNTH"],
      ["Marketing Lead", "Campaign, media, KOLs, reporting", "ZYNTH"],
      ["WavePay Marketing", "Approvals, brand assets, product content", "Client"],
      ["WavePay Product", "Demo, specialists, activation tracking", "Client"],
      ["WavePay PR", "Spokespeople, regulatory sign-off", "Client"]]}]},

 {"heading": "KPIs & Measurement",
  "body": (
    "Measured and reported within 14 days. Where a target is missed it is written down "
    "as missed — that discipline is how the next event gets better."),
  "tables": [{"headers": ["Metric", "Target", "Method"], "rows": [
      ["Premium activation, 24h", "10% of attendees", "Unique QR tracking + WavePay data"],
      ["Premium activation, 30d", "25% increase on baseline", "WavePay internal data"],
      ["Attendance", "250 confirmed", "Check-in records"],
      ["Tier-one media", "10+ features carrying the positioning", "Press clipping review"],
      ["Media reach", "5,000,000+ impressions", "Monitoring + analytics"],
      ["Social engagement", "1,000+ mentions/shares", "Platform analytics"],
      ["Partner meetings booked", "12 on the night", "Sales team log"],
      ["VIP/partner satisfaction", "90%+", "Post-event survey"],
      ["Brand sentiment", "80%+ positive", "Sentiment analysis"]]}]},

 {"heading": "Risk Register",
  "body": "Named risks, owned and mitigated. The three that actually threaten this event are the first three.",
  "tables": [{"headers": ["Risk", "Likelihood", "Impact", "Mitigation"], "rows": [
      ["Technical failure during the reveal", "M", "H", "Redundant playback and console; the silence cue rehearsed 3x; manual fallback held by the show caller"],
      ["Low activation despite good attendance", "M", "H", "Product specialists on every table; QR at seat; 48h follow-up sequence pre-built"],
      ["Key speaker cancellation", "M", "H", "Backup speaker briefed; pre-recorded CEO segment held in reserve"],
      ["Venue double-booking", "L", "H", "Contract and deposit immediately; Novotel Yangon Max on standby"],
      ["Guest no-show rate", "M", "M", "Over-invite by 15%; personal VIP follow-up; confirm at 72h and 24h"],
      ["Budget overrun", "M", "M", "Fixed vendor contracts; 10% contingency; weekly reconciliation"],
      ["Negative coverage", "L", "H", "Consistent messaging; crisis plan; regulator briefed in advance"],
      ["Vendor non-performance", "M", "M", "Named backup per category; performance clauses"],
      ["Imported equipment delay", "M", "M", "Order by week 5; local equivalents identified"],
      ["Permit/regulatory issue", "L", "M", "Engage authorities week 1"]]}]},

 {"heading": "Cultural & Practical Considerations",
  "body": (
    "Myanmar-specific things that are invisible when they are done right and very "
    "visible when they are not.\n\n"
    "**Language.** All signage, the invitation, the keynote deck and every subtitle are "
    "bilingual. Burmese is set in Pyidaungsu at 1.4x line height and is written first, "
    "not machine-translated from English.\n\n"
    "**Calendar.** 17 September sits clear of Buddhist Lent and before Thadingyut — "
    "appropriate for a celebratory corporate event.\n\n"
    "**Hierarchy.** VIP arrival, seating and introduction order are agreed in writing "
    "with WavePay a week ahead. Regulators are greeted by a named WavePay executive, "
    "not by an usher.\n\n"
    "**Food.** Halal and vegetarian options at every station, clearly labelled in both "
    "languages. No pork at the general stations.\n\n"
    "**Traffic.** Yangon evening traffic is the single most reliable threat to a 17:30 "
    "start. Invitations state 17:15; the programme is built to absorb a 20-minute "
    "arrival tail without delaying the keynote.\n\n"
    "**Sustainability.** The stage and tunnel are modular and specified for reuse; "
    "print runs are quantity-matched to the confirmed list rather than rounded up."),
  "tables": []},

 {"heading": "Terms & Conditions",
  "body": "",
  "tables": [{"headers": ["Item", "Terms"], "rows": [
      ["Payment", CM["payment_terms"]],
      ["Currency", "All payments in MMK by bank transfer. USD shown at market rate for reference only"],
      ["Cancellation by client", "60+ days: deposit forfeited. 30–59 days: 75% payable. Under 30 days: 100% payable"],
      ["Cancellation by ZYNTH", "All payments refunded in full within 30 days"],
      ["Force majeure", "Neither party liable for failure caused by circumstances beyond reasonable control"],
      ["Scope changes", "Quoted in writing and approved before work begins"],
      ["Contingency", "Held by ZYNTH; unspent balance returned at reconciliation"],
      ["Client responsibilities", "Timely approvals, brand assets, product content, spokespeople availability"],
      ["Intellectual property", "All event assets transfer to WavePay on final payment; ZYNTH retains portfolio rights"],
      ["Reporting", "Full report within 14 days of the event"]]}]},

 {"heading": "Why ZYNTH",
  "body": (
    "**We price honestly.** This proposal is a single turnkey number with the full "
    "budget shown. Where a cost is an estimate we have marked it as unverified rather "
    "than presenting it as a quote.\n\n"
    "**We own the room, not just the deck.** ZYNTH holds every vendor contract, the run "
    "of show, and the risk register. WavePay approves and attends.\n\n"
    "**We work in both markets and both languages.** Yangon vendor reality and "
    "Singapore client standards, with Burmese written first rather than translated.\n\n"
    "**We report what happened.** Including the metrics that missed. An agency that "
    "only reports wins cannot help you improve.\n\n"
    "**What we are not.** ZYNTH is producer-led: we own concept, direction, production "
    "management and the client relationship. Filming, fabrication and AV are executed "
    "by vetted Yangon partners under our contracts. We would rather tell you that than "
    "claim an in-house studio we do not have."),
  "tables": []},
]


def main() -> int:
    problems = review({
        **{s["heading"].lower().replace(" ", "_"): s for s in SECTIONS},
        "budget": {"lines": costing.lines},
        "commercial_model": CM,
    })
    hard = [p for p in problems if "floor" in p or "not a budget" in p]
    if hard:
        print("BLOCKED:", hard)
        return 1

    paths = render_both(
        slug=SLUG, title=TITLE, client=CLIENT, market="Myanmar (Yangon)",
        sections=SECTIONS,
        one_line_ask=(f"Approve {PRICE:,.0f} MMK and a "
                      f"{CM['deposit_mmk']:,.0f} MMK deposit to hold 17 September."),
        estimated_value=f"{PRICE:,.0f} MMK (USD {CM['client_price_usd']:,.0f})",
    )
    print(f"sections   : {len(SECTIONS)}")
    print(f"cost base  : {costing.cost_base_mmk:,.0f} MMK")
    print(f"price      : {PRICE:,.0f} MMK  ({CM['margin_pct']}% {CM['band'].upper()})")
    for k, v in paths.items():
        print(f"{k:10s} : {v}  ({v.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
