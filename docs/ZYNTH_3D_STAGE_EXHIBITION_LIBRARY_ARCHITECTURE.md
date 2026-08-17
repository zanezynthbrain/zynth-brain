# ZYNTH 3D Stage & Exhibition Design Library Architecture

## Purpose

This library turns ZYNTH’s spatial-design capability into a reusable, client-reviewable portfolio system for Myanmar and Singapore. Each design is stored as a complete concept package rather than as an isolated render. The minimum unit is one **Design Package ID** connecting a creative territory, client-grade proposal, visual previews, Blender/source requirements, spatial feasibility notes, indicative budget, revision history, approval state and final export set.

All concepts begin in the internal **Explore** or **Propose** work band. A visual preview is not a structural, electrical, fire-safety, rigging, permit or fabrication drawing. No client presentation, vendor RFQ, fabrication, venue booking, spend or publication is authorised without founder approval and the relevant technical review.

## Event and Spatial Taxonomy

| Portfolio family | Event types covered | Signature design opportunities |
|---|---|---|
| Corporate and leadership | Annual general meeting, conference, keynote, town hall, awards, internal culture day | Immersive keynote stage, modular content architecture, executive reveal, ceremony lighting |
| Product and brand launch | FMCG, consumer electronics, automotive, healthcare, pharmaceutical, financial product, property launch | Product reveal stage, journey tunnel, hero plinth, interactive launch moment, media wall |
| Public and experiential | Public brand activation, roadshow, pop-up, mall activation, city installation | Modular street-facing pavilion, participatory light object, queue-to-share journey |
| Exhibition and trade | Expo booth, trade show, B2B industrial, government pavilion, investment forum | Reusable modular booth, demo theatre, meeting pods, product lab, lead-capture spine |
| Sponsorship and sports | Sports sponsorship, fan zone, tournament, cultural sponsorship, concert sponsorship | Sponsor visibility system, fan-stage, trophy moment, photo/share zone, hospitality deck |
| Hospitality and destination | Hotel launch, restaurant opening, tourism event, resort experience, destination showcase | Arrival portal, dining theatre, projection environment, sunset stage, guest journey |
| Festivals and culture | Thingyan, Thadingyut, Tazaungdaing, Christmas/New Year, national days, cultural festivals | Respectful light language, community stage, procession gateway, family participation zones |
| Social impact and healthcare | Health education, NGO programme, public-service campaign, patient/community forum | Clear information stage, accessible consultation zone, calm trust environment, privacy-aware flow |
| Education and youth | University fair, school event, creator festival, youth programme, graduation | Interactive learning stage, projection classroom, creator arena, graduation identity system |
| Media and entertainment | Concert, live show, music festival, e-sports, film premiere, content studio | Performance stage, LED architecture, camera sightline system, backstage and audience energy |
| Hybrid and digital | Virtual event, hybrid conference, livestream, digital product launch | Broadcast-first set, camera-safe stage, virtual extension, remote participation layer |
| Retail and commercial property | Retail opening, showroom, property sales gallery, real-estate launch | Arrival landmark, sales theatre, model-display architecture, guided conversion route |

## Portfolio Production Waves

The library should be built in waves so quality remains credible. Wave 1 consists of six portfolio anchors: a corporate keynote stage, an FMCG product launch, a Myanmar/Singapore exhibition booth, a public brand activation, a hospitality destination stage and a healthcare/pharma education environment. Wave 2 expands into sponsorship, festival, education, entertainment, hybrid and property systems. The designs can be adapted across categories only when their underlying spatial mechanism remains buildable and strategically relevant.

## Required Package for Every Design ID

Each package contains the following linked components:

| Component | Required content |
|---|---|
| Decision record | Objective, audience, market, work band, owner, evidence state, decision required |
| Territory sheet | Three distinct territories, insight, proposition, visual world, signature moment, risk, production implication |
| Client proposal | Executive summary, concept, goals, experience journey, scope, deliverables, schedule, staffing, budget, KPI, risk and approval gates |
| 3D visual set | Hero wide, audience view, operational/sightline view, plan/orthographic view and detail/mood frame |
| Spatial pack | Site/dimension assumptions, guest flow, zones, accessibility, power/AV/rigging, back-of-house, safety dependencies and buildability notes |
| Source pack | Versioned `.blend` requirement, collection hierarchy, camera/light notes, rights-cleared asset log and export matrix |
| Showable exports | Client-safe PNG/JPG previews, optional PDF concept pack, optional `.glb`/`.fbx` after scale and axis checks |
| Commercial record | Myanmar/Singapore planning band, exclusions, pass-through assumptions, RFQ inputs, margin watchpoints |
| Governance record | Founder approval state, client-release state, vendor-release state, QC score, rejected territories and learning note |

## Recommended Drive Structure

Existing top-level Drive folders remain authoritative:

- **Proposal Library** — complete proposals and linked proposal indexes.
- **Research** — market, venue, cultural, event and technical evidence.
- **Playbook & Reports** — architecture, standards, capability and founder operating documents.

New subfolders should be created under Proposal Library and organised by Design Package ID:

```text
Proposal Library/
  3D Stage & Exhibition Library/
    00_LIBRARY_INDEX/
    01_CORPORATE_LEADERSHIP/
    02_PRODUCT_BRAND_LAUNCH/
    03_PUBLIC_EXPERIENCE/
    04_EXHIBITION_TRADE/
    05_SPONSORSHIP_SPORTS/
    06_HOSPITALITY_DESTINATION/
    07_FESTIVAL_CULTURE/
    08_HEALTHCARE_SOCIAL_IMPACT/
    09_EDUCATION_YOUTH/
    10_MEDIA_ENTERTAINMENT/
    11_HYBRID_DIGITAL/
    12_RETAIL_PROPERTY/
```

Each category folder uses the same structure:

```text
DESIGN-ID_Name/
  00_DECISION_RECORD/
  01_PROPOSAL/
  02_TERRITORIES/
  03_VISUAL_PREVIEWS/
  04_SPATIAL_TECHNICAL_PACK/
  05_BLENDER_SOURCE/
  06_CLIENT_EXPORTS/
  07_RFQ_VENDOR_INPUTS/
  08_APPROVAL_QC/
```

## Naming Convention

Use `ZYNTH-[MARKET]-[FAMILY]-[NUMBER]_[SHORT-NAME]`, for example `ZYNTH-MM-EXH-001_Luminous-Spine` or `ZYNTH-SG-COR-002_Layered-Forum`. Files follow `YYYY-MM-DD_DESIGN-ID_Deliverable_View_V##.ext`. Every rendered image, proposal and source pack must contain the same Design Package ID.

## Quality and Release Standard

A design can be labelled **Internal Concept** when the creative mechanism and visual direction are coherent. It can be labelled **Client-Reviewable** only when the proposal, visual set, assumptions and commercial inputs are complete. It can be labelled **Production-Ready Concept** only after spatial feasibility, technical dependencies, source integrity and relevant vendor/engineer questions are recorded. None of these labels equals founder approval for external release.

The applicable quality gate scores strategic relevance, originality, brand/craft, spatial/build realism, technical integrity and governance from 1–5. Client-reviewable work requires 4 or higher on every mandatory dimension and a named reviewer. Any design containing real brand assets, health claims, cultural claims, venue dimensions, sponsor marks or production commitments must pass the corresponding verification and founder gates first.

## Initial Design IDs

| ID | Market | Family | Working title | First deliverable |
|---|---|---|---|---|
| ZYNTH-MM-COR-001 | Myanmar | Corporate and leadership | The Living Forum | Keynote stage, plan and audience sightline set |
| ZYNTH-MM-LAU-001 | Myanmar | Product and brand launch | The Reveal Spine | Product-launch stage and journey tunnel |
| ZYNTH-MM-EXH-001 | Myanmar | Exhibition and trade | The Luminous Spine | Modular booth with demo theatre and meeting pods |
| ZYNTH-MM-PUB-001 | Myanmar | Public and experiential | City Pulse Pavilion | Roadshow/pop-up activation system |
| ZYNTH-MM-HOS-001 | Myanmar | Hospitality and destination | Monsoon Arrival | Hotel/destination launch environment |
| ZYNTH-MM-HCR-001 | Myanmar | Healthcare and social impact | Clear Care Forum | Accessible healthcare education stage and consultation route |
| ZYNTH-SG-EXH-001 | Singapore | Exhibition and trade | Proof-to-Pipeline Lab | B2B/industrial modular expo system |
| ZYNTH-SG-COR-001 | Singapore | Corporate and leadership | The Layered Forum | Hybrid leadership conference stage |

## Immediate Decisions Required

The founder needs to approve only the first portfolio wave and whether the initial visuals should remain neutral spec concepts or use a named client/category. Until approval, all designs remain internal hypotheses. Site dimensions, brand kits, logos, product details, sponsor marks, final copy, claims, fabrication quotes and venue constraints remain assumptions unless separately verified.
