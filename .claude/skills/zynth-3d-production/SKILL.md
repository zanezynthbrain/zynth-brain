---
name: zynth-3d-production
description: Provides professional-grade 3D spatial design, exhibition booth standards, stage design workflows, and Blender Python automation logic for the ZYNTH AI agent.
author: Manus AI
version: 1.0
---

# ZYNTH 3D Production & Spatial Design Skill

## ZYNTH Operating Contract

Follow the shared [ZYNTH Capability System Standard](../../../docs/ZYNTH_CAPABILITY_SYSTEM_STANDARD.md). In particular: classify the work band; separate verified facts from assumptions; create three distinct territories for material creative work; make output executable and measurable; pass the relevant quality gate; and preserve founder/project-owner approval before external release, spend, client contact, vendor commitment, or publication.


This skill empowers the ZYNTH AI agent to function as a professional 3D Architect and Spatial Designer. It provides the deep domain knowledge required to generate high-fidelity 3D models of exhibition booths, event stages, and experiential spaces using Blender 3D.

## How to Use This Skill

When the user requests a 3D design (e.g., "design a 6x6m tech exhibition booth"), the agent should use this skill to:
1.  **Analyze the Brief**: Identify dimensions, themes, and functional requirements.
2.  **Consult Standards**: Load reference files for booth regulations and spatial ergonomics.
3.  **Map Thematic Parameters**: Translate the design concept into specific materials, lighting, and color values.
4.  **Generate Blender Logic**: Create the Python script logic to be executed via the Blender MCP.

## Skill Pillars

### 1. Exhibition Booth Design
- **Inline, Island, and Peninsula Booths**: Standards for dimensions and height restrictions.
- **Zoning**: Strategic placement of reception, presentation, and networking areas.

### 2. Stage & AV Production
- **Sightline Optimization**: Ensuring unobstructed views for all audience members.
- **Lighting Design**: Professional 3-point and wash lighting setups with specific angles.

### 3. Blender Python Automation
- **PBR Material Generation**: Scripting high-quality materials (metal, glass, fabric).
- **Procedural Layouts**: Programmatically placing trusses, screens, and furniture.

## Reference Files

Detailed knowledges and SOPs are stored in the `3d/references/` directory:

- [TD.1. Exhibition Booth Standards](3d/references/TD_1_Exhibition_Booth_Standards.md)
- [TD.2. Stage & AV Design Fundamentals](3d/references/TD_2_Stage_AV_Design.md)
- [TD.3. Blender Automation & Python Logic](3d/references/TD_3_Blender_Automation_Logic.md)
- [TD.4. Thematic Spatial Mapping Framework](3d/references/TD_4_Thematic_Spatial_Mapping.md)
- [TD.5. Spatial Ergonomics & Traffic Flow](3d/references/TD_5_Spatial_Ergonomics_Flow.md)

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
