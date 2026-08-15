# ZYNTH Design and 3D Production Package

Read this reference when work includes a final visual system, image preview, product render, stage/booth/retail design, Blender file, or any asset that may be handed to a client, producer, vendor, printer, or fabricator.

## 1. Brief and Decision Record

Every package starts with a dated decision record.

| Field | Required content |
| --- | --- |
| Project and owner | Project ID/name, client, market, account/PM/creative owner, current work band. |
| Commercial objective | One outcome; never “make it look premium” without a business purpose. |
| Audience/use context | Who encounters it, where, device/site/light condition, decision/funnel moment. |
| Source truth | Brand kit link/version, supplied product/site files, reference image rights, verified copy/claims. |
| Constraints | Budget range, delivery date, vendor/venue, production/fabrication, localisation, accessibility, legal and rights needs. |
| Decision required | Select territory, approve preview, approve final layout, release to vendor/client, or archive. |
| Evidence state | Confirmed / supplied / assumption / validate before external use. |

## 2. Territory Sheet

Create one page per territory before a direction is selected.

| Section | Required answer |
| --- | --- |
| Territory name | A memorable internal name, not an adjective list. |
| Tension and proposition | What audience tension does this answer; what should they believe or do? |
| Creative world | The visual/spatial metaphor, material and light logic, rhythm, composition and emotional temperature. |
| Signature expression | The one frame, moment, object, interaction, or spatial reveal that makes it memorable. |
| System | How it adapts across the required formats/channels/experience touchpoints. |
| Build/generation method | Composition, photography, OpenArt preview, Blender, vendor fabrication, or mixed approach. |
| Feasibility | Time, cost, rights, data, site, safety and localisation implication. |
| Risk | Cliché, audience mismatch, brand conflict, technical unknown or culturally sensitive element. |

## 3. Image Preview Record

Use this for any image-model or OpenArt output.

| Field | Record |
| --- | --- |
| Prompt version | Date, author, model/provider if known, version number, seed/settings if available. |
| Input/reference assets | File path, permission/rights status, brand kit version, product/site source. |
| Intended use | Internal exploration, client concept frame, social background, texture, etc. |
| Required frame | Ratio, camera/perspective, main focal point, composition, subject, light/material/style. |
| Brand overlay plan | Typography/logo/legal copy applied separately in editable composition software. |
| Exclusions | Text/logos/likeness/unsafe/unsupported claim/product details that must not be generated. |
| QC result | Pass / revise / reject with reason and reviewer. |

## 4. Blender File Protocol

This protocol applies to client-ready 3D concept work. It does not make a creative model a structural or safety-approved construction drawing.

### Scene configuration

- Set declared world units and model scale. State any unknown or estimated dimensions in the scene notes and delivery document.
- Use a clean collection hierarchy: `00_REFERENCE`, `01_ARCHITECTURE`, `02_SCENIC`, `03_BRAND_PLACEHOLDERS`, `04_FURNITURE`, `05_LIGHTING`, `06_CAMERAS`, `07_OUTPUT`, `99_ARCHIVE`.
- Name objects for their function, not by default Blender names. Example: `STG_MainDeck_12000x6000`, `LED_CenterWall_7680x4320`, `CAM_HeroWide_V03`.
- Separate structural/venue assumptions from scenic/brand concepts. Use placeholders for unverified logos, products or sponsor marks.
- Use only rights-cleared textures and models. Preserve source/attribution information in a project note.

### Camera and lighting

- Include at minimum one hero camera, one audience/guest perspective, one operational/sightline perspective, and one plan/orthographic view when spatial decisions matter.
- State lens, camera height, target, colour-management setting, render engine, output resolution and sample/noise settings.
- Light for the intended condition: daylight, show mode, retail, keynote, or night. A single attractive render cannot prove the space works in use.

### Exports and source files

| File | Required check |
| --- | --- |
| `.blend` | Opens without missing critical links; collections/names clean; texture/source ownership known; version/date in filename. |
| `.png`/`.jpg` renders | Correct resolution/aspect, no unreadable/incorrect text, colour and crop checked, revision label in delivery log. |
| `.glb`/`.fbx` | Units, scale, axes, texture embedding/path, material count and import test documented. |
| `.pdf` concept pack | Plan/zone labels, assumptions, material notes, camera/render captions, source/revision list. |

Recommended filename pattern: `YYYY-MM-DD_Project_Deliverable_ViewOrFormat_V##.ext`.

## 5. Spatial Feasibility Sheet

| Area | Minimum question |
| --- | --- |
| Site and scale | What are confirmed site dimensions, height, loading, rigging and power constraints? What is assumed? |
| Guest flow | Where do guests enter, queue, dwell, interact, sit/stand, exit, and access services? |
| Sightlines | What can key audience segments see; what blocks a screen/stage/product? |
| Operations | Where are tech control, talent, storage, loading, green room, catering, registration, security and waste handled? |
| Accessibility | What route, viewing, counter/interaction, captioning, wayfinding or assistance needs apply? |
| Safety | What needs qualified engineer/vendor/venue approval: structure, electrics, fire, egress, rigging, crowd/traffic, weather? |
| Build and cost | What material, finish, labour, lead-time and fabrication choices drive cost/risk? |

## 6. Final QC and Handoff

Before the package moves outside the creative team, confirm:

- The selected territory and brand direction are approved by the correct owner.
- All text, logo, legal copy, product details and claims come from verified sources and are composed outside image/video models.
- The client pack distinguishes render/concept, indicative scope, confirmed dimensions, vendor quote, and final build documents.
- The source file, previews, exports, prompt/reference log, right-to-use notes and revision log are in the project folder.
- The next owner has a clear decision: creative approval, production estimate/RFQ, technical validation, client presentation, or release.
