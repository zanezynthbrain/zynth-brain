---
name: zynth-sponsorship-value
description: Provides specialized methods and SOPs for developing sponsorship strategies, valuing campaigns, articulating client benefits, and demonstrating clear ROI for ZYNTH Agency projects. Use this skill when seeking sponsorships, selling campaigns, or creating compelling value propositions for clients.
---

# ZYNTH Agency: Sponsorship & Value Proposition Skill

This skill enables the AI agent to develop robust sponsorship strategies, articulate compelling value propositions, and clearly demonstrate the benefits and ROI for clients and potential sponsors.

## 1. Capabilities:
- Sponsorship Strategy Development
- Campaign Valuation & ROI Articulation
- Client Benefit & Value Proposition Crafting
- Sponsorship Package Creation & Negotiation
- Post-Campaign Value Reporting

## 2. AI Integrations:
- AI for identifying potential sponsors based on brand alignment and audience demographics.
- Predictive AI models for valuing sponsorship packages and forecasting revenue potential.
- Generative AI for crafting compelling value propositions and benefit statements.
- AI for analyzing past campaign data to demonstrate ROI.
- AI-powered tools for creating customized sponsorship proposals.

## 3. Specialized Methods & SOPs:

To access the detailed Standard Operating Procedures for each sponsorship and value proposition method, refer to the corresponding Markdown files in the `sponsorship/references/` directory:

- **S.1. Sponsorship Strategy Development:** Read `sponsorship/references/S_1_Sponsorship_Strategy.md`
- **S.2. Campaign Valuation & ROI Articulation:** Read `sponsorship/references/S_2_Campaign_Valuation_ROI.md`
- **S.3. Client Benefit & Value Proposition Crafting:** Read `sponsorship/references/S_3_Client_Benefit_Value_Prop.md`
- **S.4. Sponsorship Package Creation & Negotiation:** Read `sponsorship/references/S_4_Sponsorship_Package_Negotiation.md`
- **S.5. Post-Campaign Value Reporting:** Read `sponsorship/references/S_5_Post_Campaign_Value_Reporting.md`

---

## ZYNTH guardrails (added on adoption — these override anything above)
- **R1–R5 financial law** is in `backend/knowledge/01_zynth_services.md` and is
  injected into every agent. 35% margin floor · 50% deposit · 3-month runway ·
  80/20 revenue mix · 20% profit reinvested. Margin banding: green ≥40%,
  amber 35–39.9% (justify in writing), red <35% (blocked).
- **Markets are Myanmar + Singapore.** Not New York. Price at MARKET FX, sell
  side, and state the rate and date.
- **Bilingual:** Burmese is written FIRST and English transcreated from it.
  See `backend/knowledge/26_myanmar_ad_craft.md`. Burmese is always typeset,
  never generated inside an image or video model.
- **HITL:** nothing reaches a client, a page or an inbox without MD approval.
- **Unverified numbers** are tagged or left blank. Verification is human work.
