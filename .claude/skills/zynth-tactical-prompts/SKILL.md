---
name: zynth-tactical-prompts
description: Provides a library of high-performance AI prompts and tactical frameworks for the Claude agent to execute advanced marketing and video production methods.
author: Manus AI
version: 1.0
---

# ZYNTH Tactical Prompt Library

This skill provides the ZYNTH Master Strategist AI agent with a comprehensive library of high-performance prompts and tactical frameworks. These prompts are designed to translate strategic objectives and creative directions into actionable AI commands, enabling the agent to execute advanced marketing and video production methods with precision and impact.

## How to Use This Skill

When the Claude agent needs to generate content, analyze data, or orchestrate a production task according to the "Master Tactical Methods" defined in other ZYNTH skills, it should refer to this library. Each prompt is designed to be highly effective with generative AI models, ensuring the output aligns with ZYNTH's high standards.

### Prompt Categories:

1.  **Creative Direction Prompts:** For generating compelling narratives, visual concepts, and mood boards.
2.  **Video Production Prompts:** For directing AI video editing, motion graphics, and post-production tasks.
3.  **Marketing Strategy Prompts:** For developing audience segmentation, messaging architecture, and campaign pillars.
4.  **Financial & Sponsorship Prompts:** For generating profit plans, ROI projections, and sponsorship value propositions.

## Reference Prompts

Detailed tactical prompts are stored in the `prompts/references/` directory. The Claude agent should load the relevant prompt based on the specific task and the "Master Tactical Method" being applied.

- [TP.1. The Transformation Hook Prompt](prompts/references/TP_1_Transformation_Hook.md)
- [TP.2. High-Impact Opener Prompt](prompts/references/TP_2_High_Impact_Opener.md)
- [TP.3. Automated Focus Direction Prompt](prompts/references/TP_3_Automated_Focus_Direction.md)
- [TP.4. Process-to-Result Pacing Prompt](prompts/references/TP_4_Process_to_Result_Pacing.md)
- [TP.5. Thematic Visual Layering Prompt](prompts/references/TP_5_Thematic_Visual_Layering.md)
- [TP.6. Logic-to-Result Mapping Prompt](prompts/references/TP_6_Logic_to_Result_Mapping.md)
- [TP.7. The Ecosystem View Prompt](prompts/references/TP_7_Ecosystem_View.md)

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
