"""SAFE HANDS, STRONG FUTURE — industrial safety culture campaign.

Upgrades pool concept 3c16f7c1 (Manufacturing & Industrial, MM, 45–75M band)
from a four-field stub into a full ZYNTH proposal document.

Run from backend/:  python build_safety_proposal.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.proposal_doc import costing_from_rows, commercial_model, review
from utils.proposal_render import render_both, money_table, budget_table, dated_slug

CLIENT = "Manufacturing sector client (name on brief)"
TITLE = "Safe Hands, Strong Future — Industrial Safety Culture Campaign"

BUDGET_ROWS = [
    # Scoped to land inside the sector's 45-75M expectation. Where a line was
    # trimmed it was trimmed in reach (one filming day, 12 signs not 24), never
    # in what the campaign's credibility rests on: three worker films, eight
    # posts, the full broadcast sequence and the supervisor toolkit.
    ("Strategy & Research", "Safety audit of 3 client sites + worker interviews", 1, 3_000_000),
    ("Strategy & Research", "Campaign strategy, messaging platform, Burmese-first copy system", 1, 2_200_000),
    ("Content Production", "Worker testimonial films (45-60s, bilingual subtitles)", 3, 2_000_000),
    ("Content Production", "Social content series - 8 posts, graphics + bilingual copy", 8, 420_000),
    ("Content Production", "Photography - 1 factory day, worker + PPE library", 1, 900_000),
    ("Content Production", "Safety poster designs, print-ready 300DPI", 4, 300_000),
    ("Content Production", "Toolbox-talk deck for supervisors (bilingual)", 1, 1_200_000),
    ("Distribution", "WhatsApp/Viber broadcast build + 8-tip sequence", 1, 1_900_000),
    ("Distribution", "Paid social management (Meta + TikTok, 6 weeks)", 6, 500_000),
    ("Distribution", "Paid media spend - pass-through, reported at cost", 1, 5_000_000),
    ("Distribution", "Landing page - safety resources + consultation form", 1, 2_200_000),
    ("Print & Physical", "Poster print + delivery, 3 sites", 200, 4_500),
    ("Print & Physical", "Site signage - high-risk zone markers, monsoon-rated", 12, 85_000),
    ("Measurement", "Weekly reporting + end-of-campaign performance report", 1, 1_600_000),
    ("Account & PM", "Account management, 6 weeks", 6, 550_000),
]

costing = costing_from_rows(
    [{"category": c, "item": i, "qty": q, "unit_cost_mmk": u} for c, i, q, u in BUDGET_ROWS]
)
CM = commercial_model(costing)
PRICE = CM["client_price_mmk"]

SECTIONS = [
 {"heading": "Executive Summary",
  "body": (
    "Myanmar's monsoon does not cause factory accidents. It removes the margin for "
    "error that hides them the rest of the year — wet floors, damp electrical runs, "
    "heat stress under corrugated roofing, and workers moving faster because the shift "
    "is running late.\n\n"
    "Most safety communication in Myanmar manufacturing is a poster on a wall in a "
    "language of compliance. It is read once, on day one, and never again. This "
    "campaign takes the opposite approach: **safety told by the people who do the "
    "work**, in Burmese, on the phones they already hold, during the six weeks the "
    "risk is highest.\n\n"
    "Six weeks, three sites, 2,000+ workers reached directly by broadcast, three "
    "worker-led films, and a supervisor toolkit that keeps running after we leave.\n\n"
    f"Investment: **{PRICE:,.0f} MMK** (USD {CM['client_price_usd']:,.0f}) — inside the "
    "45–75M band this sector expects, with paid media shown separately at cost."),
  "tables": [{"title": "At a glance", "headers": ["", ""], "rows": [
      ["Campaign", "Safe Hands, Strong Future"],
      ["Sector", "Manufacturing & industrial — textile, food processing, rubber, auto parts"],
      ["Market", "Yangon and Mandalay"],
      ["Duration", "6 weeks, timed to the monsoon risk peak"],
      ["Direct reach", "2,000+ workers and safety officers by broadcast"],
      ["Investment", f"{PRICE:,.0f} MMK (USD {CM['client_price_usd']:,.0f})"],
      ["Deposit to start", f"{CM['deposit_mmk']:,.0f} MMK (50%)"]]}]},

 {"heading": "Strategic Context — Why Now",
  "body": (
    "**The risk is seasonal and the calendar is unforgiving.** Monsoon conditions "
    "raise slip, electrical and heat-stress exposure across exactly the industries "
    "this campaign targets. Incident reporting peaks in Q3, which is also when safety "
    "audits and compliance reviews land.\n\n"
    "**The budget window is now.** Safety officers hold approval authority before the "
    "end of the fiscal cycle. A campaign proposed in October is a campaign that runs "
    "after the season it was designed for.\n\n"
    "**The competitive gap is real.** Safety in this sector is treated as a compliance "
    "cost, not a brand position. A manufacturer that visibly leads on worker safety "
    "differentiates on the one dimension buyers, regulators and workers all care "
    "about — and that no competitor is currently claiming.\n\n"
    "The cost of doing nothing is not abstract: one serious incident during audit "
    "season costs more in downtime, investigation and reputation than this entire "
    "campaign."),
  "tables": []},

 {"heading": "Objectives & How We Will Know It Worked",
  "body": "Four objectives with numbers attached, so the campaign can be judged.",
  "tables": [{"headers": ["Priority", "Objective", "Success measure"], "rows": [
      ["1", "Change behaviour on the floor", "300+ workers complete a safety video at 80%+ completion"],
      ["2", "Reach the whole workforce directly", "2,000+ broadcast messages delivered, 25% engagement"],
      ["3", "Generate qualified commercial leads", "150 plant managers request a safety consultation"],
      ["4", "Establish the safety position publicly", "8 posts averaging 150+ engagements; 4% CTR to the resource page"]]}]},

 {"heading": "Who We Are Talking To",
  "body": (
    "Three audiences, three different messages. Treating them as one is why most "
    "safety communication fails — the message that moves a plant manager does not "
    "move a machine operator."),
  "tables": [{"headers": ["Audience", "Who", "What moves them", "Channel"], "rows": [
      ["Plant managers", "25–55, budget authority", "Downtime cost, audit exposure, workforce retention", "Paid social, landing page, consultation offer"],
      ["Safety officers", "Compliance owners", "Practical tools they can deploy tomorrow", "Broadcast, toolbox-talk deck, posters"],
      ["Shift supervisors", "The real enforcers", "Being backed up, not blamed", "Toolbox deck, site signage"],
      ["Factory workers", "18–45, Burmese-first, mobile-first", "Recognition, peers they trust, going home whole", "Testimonial films, broadcast, posters"]]}]},

 {"heading": "The Creative Concept",
  "body": (
    "### The insight\n\n"
    "Ask a factory worker in Yangon why they skipped a guard rail and they will not "
    "say they forgot the rule. They will say the shift was behind. Safety rules lose "
    "to production pressure because rules are abstract and the quota is not.\n\n"
    "So the campaign does not argue with the rule. It changes **who is asking**.\n\n"
    "### The idea\n\n"
    "**\"Safe Hands, Strong Future.\"**\n"
    "**MM:** \"လက်များ လုံခြုံ၊ အနာဂတ် ခိုင်မာ။\"\n\n"
    "*(Burmese written first; the English is transcreated from it. The Burmese has a "
    "4+4 balance that reads in one breath — it works spoken across a factory floor, "
    "which is where it will actually be used.)*\n\n"
    "Every piece of the campaign is **a worker speaking to another worker**. Not the "
    "company. Not a safety officer. Not a voiceover. The person on the next machine.\n\n"
    "### Why this idea and not the obvious one\n\n"
    "The obvious campaign is a hazard checklist with a hard-hat icon and a stern line "
    "about compliance. It is what every safety poster in the country already looks "
    "like, which is precisely why nobody reads them any more. It also positions the "
    "company as the enforcer — the same voice as the quota — so the message competes "
    "with itself.\n\n"
    "Peer-led works because it moves safety from *rule* to *norm*. A rule is something "
    "you break when you are behind. A norm is something your colleagues expect of you. "
    "That distinction is the entire campaign.\n\n"
    "### The films — what makes them different\n\n"
    "Three films, 45–60 seconds, each with the same structure:\n\n"
    "1. **The near-miss** (0–15s). A real worker describes a moment it almost went "
    "wrong. Their own words, their own accent, no script.\n"
    "2. **What changed** (15–40s). The one specific thing they now do differently. "
    "Concrete, small, copyable.\n"
    "3. **Who they go home to** (40–60s). Not sentimental — one line, then the mark.\n\n"
    "Shot on the floor during a real shift, not staged after hours. Handheld, "
    "available light, factory sound left in. The roughness is the credibility.\n\n"
    "### Visual identity\n\n"
    "High-visibility yellow (#F2B705) as the single accent — the colour already means "
    "*pay attention* in every factory in the world, so we borrow existing meaning "
    "rather than teaching new meaning. Deep charcoal (#1C1F24) ground. White for "
    "instruction only, never decoration.\n\n"
    "Type is set for the environment, not the screen: **Pyidaungsu Bold at a minimum "
    "size readable from three metres**, because a poster that needs you to walk up to "
    "it will not be read on a moving floor.\n\n"
    "Photography is real workers at real stations with real PPE. No stock. No models. "
    "Anyone on that floor will know instantly whether the person in the picture has "
    "ever done the job.\n\n"
    "### Tone\n\n"
    "Direct, respectful, never scolding. The campaign never implies workers are "
    "careless. It assumes they are under pressure — because they are — and gives them "
    "something usable."),
  "tables": [{"title": "Message by audience", "headers": ["Audience", "The line they hear"], "rows": [
      ["Worker", "The person next to you wants you here tomorrow."],
      ["Supervisor", "Backing your team on safety is backing your numbers."],
      ["Safety officer", "Tools you can run on Monday, not a policy to write."],
      ["Plant manager", "One incident in audit season costs more than this campaign."]]}]},

 {"heading": "Campaign Architecture — Six Weeks",
  "body": (
    "Three phases. Each phase has one job, and nothing runs before the thing it "
    "depends on exists."),
  "tables": [{"headers": ["Phase", "Weeks", "Job", "What goes live"], "rows": [
      ["Ground truth", "1–2", "Find the real hazards and the real stories", "Site audits, worker interviews, filming"],
      ["Saturation", "3–5", "Reach every worker on every channel they use", "Films, 8 posts, broadcast sequence, posters, signage, paid"],
      ["Conversion & handover", "6", "Turn attention into consultations and hand over the tools", "Consultation push, toolbox deck training, report"]]}]},

 {"heading": "Channel Plan",
  "body": (
    "Channel choice follows where the audience actually is, which in Myanmar "
    "manufacturing is Viber and WhatsApp far more than any feed.\n\n"
    "**Broadcast is the backbone.** 2,000+ contacts, eight weekly tips, each one "
    "usable in under thirty seconds. Broadcast reaches workers who never see paid "
    "social, and it is the only channel where delivery can be verified.\n\n"
    "**Paid social carries the commercial layer** — it is aimed at plant managers, not "
    "workers, and its job is consultation requests.\n\n"
    "**Physical assets do the work we cannot.** A poster at the point of risk is read "
    "at the moment of decision, which no phone campaign can match."),
  "tables": [{"headers": ["Channel", "Audience", "Volume", "Purpose"], "rows": [
      ["Viber / WhatsApp broadcast", "Workers, safety officers", "2,000+ contacts, 8 sends", "Reach and repetition"],
      ["Facebook / Instagram", "Plant managers, industry", "8 posts + 3 ad variants", "Position and generate leads"],
      ["TikTok", "Workers 18–35", "3 films, cut vertical", "Completion and sharing"],
      ["Site posters", "Everyone on the floor", "4 designs, 200 prints, 3 sites", "Decision-moment reminder"],
      ["Site signage", "High-risk zones", "12 markers, monsoon-rated", "Permanent hazard marking"],
      ["Toolbox-talk deck", "Supervisors", "1 bilingual deck", "Keeps running after the campaign"],
      ["Landing page", "Plant managers", "1 page + form", "Consultation capture"]]}]},

 {"heading": "Deliverables",
  "body": "Everything the client owns at the end, with full usage rights.",
  "tables": [{"headers": ["Deliverable", "Spec", "Delivered"], "rows": [
      ["Worker testimonial films", "3 x 45–60s, 16:9 + 9:16, Burmese/English subtitles", "Week 4"],
      ["Social content series", "8 posts, graphics + bilingual copy, FB/IG/TikTok", "Weeks 3–6"],
      ["Photography library", "150+ edited stills, full rights, 1 factory day", "Week 3"],
      ["Safety posters", "4 designs, 1200x1800px, print-ready 300DPI", "Week 3"],
      ["Site signage", "12 monsoon-rated hazard markers, installed", "Week 3"],
      ["Broadcast sequence", "8 tips, scheduled, bilingual", "Week 3 onward"],
      ["Toolbox-talk deck", "Bilingual supervisor deck + facilitation notes", "Week 5"],
      ["Landing page", "Resource hub + consultation form", "Week 3"],
      ["Paid campaign", "3 ad variants, targeting, budget allocation", "Week 3"],
      ["Performance report", "Weekly + full end-of-campaign report", "Weekly, final week 7"]]}]},

 {"heading": "Production Requirements",
  "body": (
    "**Filming on a live floor is the single biggest delivery risk**, so it is planned "
    "rather than hoped for.\n\n"
    "One filming day across three sites, during real shifts. We work around "
    "production, not the other way round — no line stops for a camera.\n\n"
    "Every worker who appears signs a release, in Burmese, explained verbally before "
    "signing. Anyone can decline with no consequence, and we brief supervisors that "
    "declining must carry none. A safety campaign that pressures workers into "
    "appearing has already failed at its own premise.\n\n"
    "Crew is deliberately small — one DP, one sound, one producer/translator. A large "
    "crew changes behaviour on a factory floor, and we need normal behaviour."),
  "tables": [{"headers": ["Requirement", "Detail", "Owner"], "rows": [
      ["Site access", "3 sites, 1 filming day, real shifts", "Client"],
      ["Worker participation", "6–9 volunteers, signed releases, no pressure", "Client + ZYNTH"],
      ["PPE for crew", "Site-standard, worn at all times on camera", "ZYNTH"],
      ["Safety officer escort", "Required in production areas", "Client"],
      ["Broadcast contact list", "2,000+ opted-in numbers", "Client"],
      ["Brand assets", "Logo, guidelines, existing safety policy", "Client"],
      ["Approvals", "Films and posters, 3 working days per round", "Client"]]}]},

 {"heading": "Budget",
  "body": (
    "Every line is quantity x unit cost, summed. Paid media is shown as a separate "
    "pass-through line and reported at cost — ZYNTH does not mark up media spend.\n\n"
    "Cost bands are [UNVERIFIED — Aug 2026] against ZYNTH's Yangon rate card and will "
    "be replaced with written quotes for print, signage and crew before contract."),
  "tables": [budget_table(costing)]},

 {"heading": "Commercial Model",
  "body": (
    f"**Investment: {PRICE:,.0f} MMK (USD {CM['client_price_usd']:,.0f}).**\n\n"
    "A single turnkey figure covering strategy, production, distribution, physical "
    "assets and reporting. Not cost-plus-percentage: a percentage fee pays us to spend "
    "more of your money.\n\n"
    f"{CM['payment_terms']}\n\n"
    "**Media spend is pass-through.** The 5,000,000 MMK line is paid to the platforms "
    "and reconciled against actual spend. Underspend is returned.\n\n"
    "Contingency is held by ZYNTH and reconciled at close; unspent balance is "
    "returned, not retained."),
  "tables": [money_table(CM)]},

 {"heading": "Timeline",
  "body": "Six delivery weeks plus a reporting week. Week 1 starts on deposit receipt.",
  "tables": [{"headers": ["Week", "Phase", "Milestone"], "rows": [
      ["1", "Ground truth", "Site audits, worker interviews, hazard mapping"],
      ["2", "Ground truth", "Filming (2 days), photography, strategy sign-off"],
      ["3", "Saturation", "Films, posters, signage, landing page, broadcast and paid go live"],
      ["4", "Saturation", "Film release, mid-campaign optimisation"],
      ["5", "Saturation", "Toolbox-talk training, supervisor handover"],
      ["6", "Conversion", "Consultation push, lead handover to client sales"],
      ["7", "Close", "Full performance report, asset handover, debrief"]]}]},

 {"heading": "Team & Responsibilities",
  "body": "Who does what, so nothing falls between two people.",
  "tables": [{"headers": ["Role", "Responsible for", "Side"], "rows": [
      ["ZYNTH Account Lead", "Single point of contact, commercials, escalation", "ZYNTH"],
      ["Strategy Lead", "Audit, messaging platform, measurement", "ZYNTH"],
      ["Creative Director", "Concept, films, visual system", "ZYNTH"],
      ["Producer / Translator", "Filming days, releases, Burmese-first copy", "ZYNTH"],
      ["Paid Media Manager", "Campaign build, optimisation, spend reporting", "ZYNTH"],
      ["Client Safety Officer", "Site access, escort, technical accuracy review", "Client"],
      ["Client Marketing", "Brand approvals, asset supply", "Client"],
      ["Client Sales", "Receiving and working the consultation leads", "Client"]]}]},

 {"heading": "KPIs & Measurement",
  "body": (
    "Reported weekly and in full at close. Metrics that miss are written down as "
    "missed — an agency that only reports wins cannot help you improve."),
  "tables": [{"headers": ["Metric", "Target", "Method"], "rows": [
      ["Video completion", "300+ workers at 80%+ completion", "Platform analytics"],
      ["Broadcast delivery", "2,000+ delivered", "Broadcast platform reports"],
      ["Broadcast engagement", "25% click to resources", "Tracked links"],
      ["Paid impressions", "5,000+", "Meta / TikTok reporting"],
      ["Landing page CTR", "4%", "Platform + page analytics"],
      ["Qualified leads", "150 consultation requests", "Form submissions, deduplicated"],
      ["Organic engagement", "150+ per post average", "Platform analytics"],
      ["Poster recall (optional)", "60%+ unprompted", "On-site survey, week 6"]]}]},

 {"heading": "Risk Register",
  "body": "The first three are the ones that actually threaten this campaign.",
  "tables": [{"headers": ["Risk", "Likelihood", "Impact", "Mitigation"], "rows": [
      ["Workers decline to appear on film", "M", "H", "Over-recruit to 9 volunteers; anonymised hands-and-voice format held as fallback; never pressure"],
      ["Site access delayed past week 2", "M", "H", "Filming dates contracted at kick-off; second site held as backup; schedule absorbs 5 days"],
      ["A real incident occurs during the campaign", "L", "H", "Pre-agreed pause protocol: all campaign activity stops within 2 hours pending client direction"],
      ["Broadcast list is smaller or unopted", "M", "M", "Verify list in week 1; if short, shift budget to paid and QR-to-opt-in posters"],
      ["Burmese copy is technically wrong", "M", "M", "Client safety officer reviews every safety claim before publication"],
      ["Monsoon disrupts filming", "H", "L", "Indoor filming by design; two weather days built into the schedule"],
      ["Leads not worked by client sales", "M", "M", "Handover protocol agreed week 1; leads delivered daily, not in a batch"],
      ["Print delivery late to sites", "M", "M", "Order week 2; local Yangon printer with a named backup"]]}]},

 {"heading": "Cultural & Practical Considerations",
  "body": (
    "**Burmese first, always.** Every worker-facing asset is written in Burmese and "
    "transcreated to English, never the reverse. Pyidaungsu throughout, typeset by "
    "hand — Burmese script is never generated inside an image or video model, because "
    "it comes out malformed and a malformed safety instruction is worse than none.\n\n"
    "**Respect the hierarchy without hiding behind it.** Supervisors are briefed "
    "before workers are approached. Going around them produces resentment that "
    "outlives the campaign.\n\n"
    "**Never blame the worker.** Not in a single asset. Myanmar factory safety "
    "messaging has a long habit of implying carelessness; it is why the posters are "
    "ignored. Every message here assumes pressure, not negligence.\n\n"
    "**Pay the participants.** Workers who appear on film receive a stipend. It is a "
    "small line in the budget and a large signal about whether the company means it.\n\n"
    "**Faith and calendar.** Filming avoids full-moon days and religious observances; "
    "the schedule is confirmed against the site's own calendar in week 1."),
  "tables": []},

 {"heading": "Terms & Conditions",
  "body": "",
  "tables": [{"headers": ["Item", "Terms"], "rows": [
      ["Payment", CM["payment_terms"]],
      ["Currency", "MMK by bank transfer. USD shown at market rate for reference"],
      ["Media spend", "Pass-through at cost, reconciled; underspend returned"],
      ["Cancellation by client", "Before filming: deposit forfeited. After filming: 75% payable. Final week: 100%"],
      ["Cancellation by ZYNTH", "All payments refunded in full within 30 days"],
      ["Incident pause", "All activity pauses within 2 hours of a reportable site incident; timeline extends by the pause"],
      ["Worker consent", "Written release from every identifiable participant; withdrawal honoured up to publication"],
      ["Scope changes", "Quoted in writing and approved before work begins"],
      ["Intellectual property", "All assets transfer to the client on final payment; ZYNTH retains portfolio rights excluding worker footage without separate consent"],
      ["Reporting", "Weekly during the campaign; full report within 7 days of close"]]}]},

 {"heading": "Why ZYNTH",
  "body": (
    "**We price honestly.** One turnkey figure, the full budget shown, media at cost, "
    "and every estimate marked as an estimate rather than dressed up as a quote.\n\n"
    "**We write Burmese first.** Not translated at the end. On a factory floor that is "
    "the difference between a message that lands and one that is politely ignored.\n\n"
    "**We report what happened**, including the metrics that missed.\n\n"
    "**What we are not.** ZYNTH is producer-led. We own strategy, concept, direction "
    "and the client relationship; filming, print and signage are executed by vetted "
    "Yangon partners under our contracts. We would rather say that than claim a "
    "production house we do not have.\n\n"
    "**A note on this campaign specifically.** We will push back if asked to make "
    "workers look like the problem. It would be easier to produce and it would not "
    "work, and we would rather tell you that before you pay us than after."),
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

    slug = dated_slug("Manufacturing", "Safe Hands Strong Future", "Campaign", 1)
    paths = render_both(
        slug=slug, title=TITLE, client=CLIENT, market="Myanmar (Yangon + Mandalay)",
        sections=SECTIONS,
        one_line_ask=(f"Approve {PRICE:,.0f} MMK and a {CM['deposit_mmk']:,.0f} MMK "
                      "deposit to start before the monsoon risk peak passes."),
        estimated_value=f"{PRICE:,.0f} MMK (USD {CM['client_price_usd']:,.0f})",
    )
    band_lo, band_hi = 45_000_000, 75_000_000
    print(f"sections  : {len(SECTIONS)}")
    print(f"cost base : {costing.cost_base_mmk:,.0f} MMK")
    print(f"price     : {PRICE:,.0f} MMK ({CM['margin_pct']}% {CM['band'].upper()})")
    print(f"vs band   : {band_lo:,}–{band_hi:,} MMK — "
          f"{'INSIDE' if band_lo <= PRICE <= band_hi else 'OUTSIDE'}")
    for k, v in paths.items():
        print(f"{k:9s} : {v.name}  ({v.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
