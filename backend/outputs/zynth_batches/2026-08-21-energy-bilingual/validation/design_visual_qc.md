# Design Visual QC

**Reviewed:** 2026-08-21 UTC

| Asset | Result | Finding | Resolution |
|---|---|---|---|
| `01_continuity-clinic_3d.png` (first render) | Failed | The preview routed English labels through a Myanmar-only font, producing unreadable English glyphs. | Font routing was corrected to use DejaVu Sans for Latin copy and Noto Sans Myanmar for Myanmar copy; all PNG previews and SVG sources were regenerated. |
| `01_continuity-clinic_3d.png` (regenerated) | Passed | English title, view headings, design labels, dimensions notes, material/lighting/furniture references and footer are legible. Myanmar title and localised view labels render as Unicode Myanmar. | Retained as representative physical-package quality standard. |

**Known limitation:** The design boards are conceptual client-viewable planning visuals. They remain non-construction, non-engineering artifacts; the packages themselves state the need for supplier engineering, venue survey, HSE review and client approvals.

| `08_my-load-my-plan_ui_experience_storyboard.png` | Passed | The five-stage mobile journey is visible end-to-end: entry, priority, context, consent and booking. The board includes UX, copy, consent, accessibility and analytics notes. | Retained as the digital-only concept storyboard standard. |
| `ZYNTH-20260821-ENERGY-Monitoring.xlsx` | Passed structural review | Workbook contains six named sheets: Overview, Concept Monitor, Approval & Risk, Assumptions, Source Log and Delivery Inventory; the renderer produced seven print pages. | Retained; formula and source assertions remain subject to final content validation. |
