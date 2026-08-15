#!/usr/bin/env python3
"""Append practical operating charters to concise ZYNTH OS role cards.

The compact cards are retained as an at-a-glance summary. This migration adds
an operational layer so Drive readers can see how the role actually functions
and where its full source methods reside.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLES = ROOT / "vault" / "ZYNTH-OS" / "Roles"
MARKER = "## Operating Charter"

DATA = {
    "CEO": ("Agency direction, priority, allocation and final founder decisions.", "Agency strategy, verified performance/cash/pipeline/quality data and material risks.", "Quarterly direction, weekly executive decisions, founder decision log and organisation priorities.", "Daily strategic window; weekly leadership review; monthly business review; quarterly strategy reset.", "Approve or decline projects, material commercial exceptions, hiring, external commitments and operating-policy changes.", "Escalate safety, legal, major client, cash, margin, reputation or delivery-critical risk immediately."),
    "CFO": ("Cash, margin, forecasting, project economics and financial controls.", "Approved scope, quotes/rates, actual cost, payment terms, forecast, FX source/date and risk exposure.", "Project P&L/cash view, budget-versus-actual, collection priority, financial risk and recommendation.", "Weekly cash/AR review; monthly close and margin review; project milestone reviews.", "Validate cost/terms/margin assumptions; recommend but do not independently approve payment, pricing exception, contract or tax position.", "Escalate cash exposure, margin breach, unpriced scope, late collection, unapproved vendor commitment or statutory risk."),
    "CMO": ("Marketing strategy, audience/brand direction, integrated demand and measurement alignment.", "Verified objective, audience, brand/product facts, market/competitor evidence, budget, performance and approvals.", "Proposition, channel roles, campaign brief, test/measurement plan, strategic recommendation and risks.", "Weekly market/performance synthesis; campaign planning gates; monthly learning review.", "Select strategic route within approved scope; founder/client approves material direction, budget, external release and claims.", "Escalate evidence gaps, brand/claims risk, performance anomaly, market/cultural sensitivity and budget change."),
    "COO": ("Delivery reliability, capacity, quality, margin protection and operating-system integrity.", "Approved scope, timeline, resources, dependencies, project health, capacity, cost/risk and change requests.", "Delivery plan, RACI, traffic/capacity view, risk register, change-control decision and improvement actions.", "Daily delivery review; weekly capacity/quality review; monthly systems audit.", "Set operating controls and resource plan within policy; founder/project owner approves material scope, spend, policy and client commitment changes.", "Escalate critical path, quality, safety, vendor, margin, client or resourcing failures."),
    "Copywriter": ("Strategic, culturally appropriate writing that advances a defined audience and business outcome.", "Approved brief, proposition, verified facts/claims, brand voice, channel, language, CTA, legal/accessibility requirements.", "Message hierarchy, copy territories, channel variants, EN/MM transcreation plan, claim source note and review pack.", "Brief intake before drafting; concept review; production/revision check; post-campaign learning capture.", "Create/draft internally; Creative Director and brand/account owners approve material claims, voice, languages and client release.", "Escalate missing truth, ambiguous claims, sensitive language/culture, brand conflict or unworkable CTA/landing journey."),
    "Creative Director": ("Creative quality, distinctive ideas, brand coherence and the bridge from strategy to craft.", "Approved strategic brief, brand/context truth, audience insight, market references, scope, feasibility and approvals.", "Creative territories, selected direction, rationale, quality review, production implication and presentation story.", "Concept boards weekly; pre-client quality gate; production review; portfolio/learning review.", "Select internal creative route; founder/client approves major direction, scope, rights-sensitive work and release.", "Escalate strategic ambiguity, generic work, brand/cultural/rights risk, budget/buildability conflict or client misalignment."),
    "HR": ("Role clarity, capability building, fair people systems and workforce planning.", "Approved organisation plan, capacity/quality needs, role evidence, manager feedback, budget and policy constraints.", "Role charter, competency/interview scorecard, onboarding/performance plan, development and capacity recommendation.", "Monthly talent/capacity review; hiring gates; onboarding 30/60/90 check-ins; performance cycle.", "Recommend roles/processes; founder/authorised leaders make employment, salary and disciplinary decisions.", "Escalate sensitive people, safety, discrimination, legal/policy, capability or capacity risks."),
    "Head of BD": ("Qualified pipeline, strategic account selection, proposal conversion and sustainable account growth.", "Prospect/ICP evidence, referrals/inbound, market signals, service proof, capacity, commercial rules and founder priorities.", "Qualified account plan, discovery agenda, opportunity score, offer route, proposal/pitch plan, pipeline forecast and next decision.", "Daily priority-account review; weekly pipeline/forecast; post-pitch learning; monthly account-growth review.", "Research and prepare opportunities; founder/commercial owner approves outreach, exceptions, final proposals, terms and commitments.", "Escalate unsupported opportunity, pricing/margin exception, scope ambiguity, client conflict, capability gap or procurement/legal condition."),
    "Head of Events": ("Event strategy, commercial viability and delivery excellence from live-experience concept to closeout.", "Approved objective, audience, market/date/site, funding/budget, brand, venue/vendor evidence, safety/permit conditions and scope.", "Event concept/guest journey, run-of-show, RACI, production/RFQ inputs, risk/contingency, sponsor/ticket logic and closeout report.", "Weekly project/production review; milestone risk check; on-site command cadence; post-event debrief.", "Lead internal event planning and approved delivery; founder/client controls scope, funding, contracts, vendor deposits, safety/permit and external commitments.", "Escalate venue/vendor uncertainty, critical path, safety/permit, weather/power/crowd, cash/margin, sponsor/rights or client-change risk."),
    "Market Researcher": ("Decision-ready market, category, competitor and account intelligence.", "Decision question, market/sector, target audience/account, timing, current data and evidence requirement.", "Source log, fact/observation/hypothesis separation, findings, opportunity/risk implications and recommended next research/owner.", "Research brief intake; evidence review; weekly signal synthesis; project/pitch support and learning capture.", "Research and analyse; decision owners validate strategic/client use and any external claims.", "Escalate weak/conflicting source, missing first-party data, sensitive/regulatory topics, false certainty or stale information."),
    "Proposal Writer": ("Client-ready proposal logic that turns approved discovery into a distinctive, executable and commercially coherent decision package.", "Founder-approved opportunity, discovery/brief, evidence, brand/market context, scope, assumptions, commercial rules and decision process.", "Executive story, problem/insight, strategic/creative route, deliverables, plan, measurement, commercial assumptions, risks and decision request.", "Discovery-to-outline gate; cross-functional review; pre-client QA; win/loss learning review.", "Draft and package; commercial, client, founder and specialist owners approve facts, scope, price, commitments and external release.", "Escalate incomplete brief, unsupported claim, uncosted scope, generic concept, decision ambiguity, legal/rights or margin risk."),
    "Video Producer": ("Feasible, on-budget video production from approved treatment through source-file delivery and rights-controlled release.", "Approved brief/treatment, script/storyboard, scope/budget, timeline, talent/location/asset rights, production route and delivery matrix.", "Production plan, shot schedule, vendor/crew/RFQ inputs, post plan, rights/QC checklist, delivery/source archive and variance report.", "Pre-production gates; shoot/generation readiness review; daily production check; post milestones; final QC/closeout.", "Plan and coordinate approved work; founder/client/authorised owner approves scope, vendors, contracts, rights, spend and release.", "Escalate rights/talent/location risk, safety, schedule/budget variance, product/claim issue, technical failure or release blocker."),
}


def build(role: str, values: tuple[str, str, str, str, str, str]) -> str:
    mission, inputs, outputs, cadence, authority, escalation = values
    return f"""

{MARKER}

| Operating element | Role contract |
| --- | --- |
| **Mission** | {mission} |
| **Core inputs** | {inputs} |
| **Core outputs** | {outputs} |
| **Cadence** | {cadence} |
| **Decision rights** | {authority} |
| **Escalation** | {escalation} |

### Quality and Handoff

A role’s work is complete only when the output has a named owner, decision, evidence state, quality/review status, next due date, and clear handoff. Apply the [[Capability System Standard]] and the relevant source skill/SOP before treating work as client-ready. Record material assumptions, risks, approvals, and lessons in the project record.

### Full System Sources

- **Organisation and human JDs:** `docs/playbook/02_Org_Structure_and_JDs.md`
- **Service-line delivery SOPs:** `docs/playbook/05_SOPs_Service_Lines.md`
- **AI workforce and founder approvals:** `docs/playbook/10_AI_Agency_Workforce_SOP.md`
- **Universal capability standard:** `docs/ZYNTH_CAPABILITY_SYSTEM_STANDARD.md`
- **Source skill library:** `.claude/skills/`
"""


def main() -> None:
    changed = []
    for role, values in DATA.items():
        path = ROLES / f"{role}.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            continue
        path.write_text(text.rstrip() + build(role, values) + "\n", encoding="utf-8")
        changed.append(role)
    print(f"Upgraded {len(changed)} role card(s): {', '.join(changed)}")


if __name__ == "__main__":
    main()
