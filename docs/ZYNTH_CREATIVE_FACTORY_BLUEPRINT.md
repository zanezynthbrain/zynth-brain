# ZYNTH Creative Factory Blueprint

**Prepared for ZYNTH**  
**Purpose:** Extend Zynth Brain into a governed agency operating system that discovers opportunities, creates distinctive work, delivers client-ready 2D/3D packages, and learns from outcomes.

## Executive Position

ZYNTH already has a credible agency foundation: a public proposition spanning digital marketing, events, video, web, brand strategy, and media buying; an existing 3D stage-design showcase; and a Zynth Brain codebase with proposal generation, knowledge grounding, approval-oriented content planning, campaign/event capabilities, outcome logging, and a live operating cadence.[1] [2] The immediate objective is therefore **not another generic chatbot**. It is a controlled **Creative Factory** that converts verified market, cultural, brand, and performance signals into three high-quality daily concept packages, then produces selected concepts as client-presentable image and 3D deliverables.

The design is deliberately outcome-led. A concept is not marked successful merely because it is attractive or technically generated. It must pass a strategic and craft review, make a measurable client proposition, and later be judged against the campaign objective. This is consistent with the WARC/ANA approach of aligning creative work to evidence, operating processes, and shared evaluation language; the IAB’s emphasis on a unified cross-channel performance view; and internationally recognized AI governance principles around traceability, human oversight, transparency, and ongoing risk management.[3] [4] [5] [6]

## Audit Findings

| Area | Confirmed strength | Material gap to close | Required action |
| --- | --- | --- | --- |
| Agency positioning | The public site articulates a multi-disciplinary, regional creative agency and showcases services from strategy through events and media. | The browser-rendered first view appeared blank, despite extractable content, which risks poor discoverability and client confidence. | Perform a front-end performance, accessibility, SEO, and device test before treating the website as a principal lead-generation surface. |
| Strategy and proposals | The repository has a substantial proposal factory, real pricing/standards knowledge, bilingual work, a client-ready proposal example, and a persistent concept pool. | The proposal library is stronger than the final delivery and measured-results layers. | Use the factory as the front end of a closed loop: brief → proposal → approved production → results → reusable learning. |
| Content production | The content studio includes strategist, content creator, design director, designer, bilingual copy support, package reconciliation, deterministic review checks, approvals, and client-facing exports. | It autonomously creates plans/specifications; it does not yet autonomously create the requested three final designs per day. | Introduce a daily creative brief, production job, quality scorecard, and asset-package record. |
| Image generation | Current source code renders images via the OpenAI Images API after founder approval and records a capped estimated cost. | The codebase does **not** currently demonstrate automated OpenArt production. | Validate the actual OpenArt connection, API/MCP capability, model choice, quotas, and output ownership before routing image jobs there. |
| 3D delivery | A real Blender Python scene-builder exists and exports `.blend`, `.glb`, and `.fbx` files. | It is a fixed AURUM/Novotel-style scene, not a general multi-industry 3D production system; other project notes describe 3D as a live-session/manual drain. | Generalize the scene builder into modular scene kits and add deterministic render, export, validation, and packaging stages. |
| Automation and safety | Scheduled research, proposals, consolidation, queued work, switches, approval gates, and a self-improvement loop already exist. | Creative rendering requires a durable execution environment and clear authority boundaries. | Separate low-risk autonomous planning from controlled creative generation, client-facing delivery, paid-media changes, and publishing. |

## Target Operating Model

The Creative Factory should operate through seven bounded agent roles. These are roles with clear contracts and audit logs, not unrestricted autonomous personas. Each agent receives only the verified information required for its task and writes structured outputs to the project record.

| Agent role | Core responsibility | Required inputs | Required output | Authority boundary |
| --- | --- | --- | --- | --- |
| **1. Opportunity Intelligence** | Maintains a rolling opportunity map across regions, sectors, cultural moments, festivals, special days, consumer trends, and client business cycles. | Market, country, industry, client, timing, verified sources. | Ranked opportunity briefs with relevance and source confidence. | May recommend opportunities; cannot invent local claims, holidays, or market facts. |
| **2. Cultural and Brand Strategist** | Translates an opportunity into a tension, audience insight, proposition, campaign objective, channel role, and success metric. | Approved opportunity brief, brand profile, cultural constraints. | One-page strategic brief with assumptions and open questions. | Stops when brand facts, legal requirements, or cultural verification are missing. |
| **3. Concept Lab** | Creates diverse campaign/event/design territories and selects a deliberately different theme for each daily brief. | Strategy brief, previous concepts, avoidance/novelty log. | Three original territories, each with rationale, key visual direction, activation/application plan, and expected business effect. | Cannot label work as a client recommendation before Creative Director review. |
| **4. Design and 3D Director** | Converts selected territories into exact art direction, media prompts, spatial/3D specifications, technical dimensions, accessibility requirements, and production budget. | Chosen concept, brand kit, destination channel/event constraints. | Production-ready design spec and either image or 3D job manifest. | Must flag feasibility, IP, typography, safety, fabrication, and missing-assets risks. |
| **5. Production Router** | Assigns each job to the correct production lane: image, deterministic compositor, Blender scene kit, video, or human designer. | Approved job manifest and capacity limits. | Time-stamped job, model/tool settings, asset paths, status, and cost/usage record. | May generate only within the daily cap and only for approved brand-safe jobs. |
| **6. Creative Quality Council** | Performs deterministic, evaluative, and human review before client release. | Rendered outputs, original brief, brand kit, technical specs. | Pass, revise, or reject decision with specific remediation instructions. | Cannot override a mandatory safety, legal, factual, or brand failure. Human Creative Director remains final release authority. |
| **7. Proposal and Results Analyst** | Packages approved work and captures outcome data after deployment. | Approved assets, scope, estimate, client objective, campaign data. | Client concept pack, source-file manifest, case-study record, and lesson candidate. | Cannot claim results without validated source data; can only promote lessons after threshold evidence. |

## Daily Creative Cadence

The requested **minimum of three designs per day** becomes a reliable agency cadence only if “design” has a defined standard. Each daily unit is one **Concept Package**, not merely a generated image. It contains an insight, client/business objective, visual or spatial idea, media specification, proposal copy, generated preview(s) where approved, and a delivery manifest.

| Time (local operating timezone) | Workflow | Output | Control |
| --- | --- | --- | --- |
| 06:30 | Opportunity scan and calendar refresh | Verified day/week/season/industry opportunity candidates | Source confidence and country/culture tags required. |
| 07:00 | Strategic filtering and variety planning | Three different daily brief slots across sector, audience, objective, and medium | Prevents repetition and avoids producing three variations of the same trend. |
| 07:30 | Concept Lab and direction | Three concept packages, each with explanation and campaign/event application | Automatic critique ranks novelty, relevance, feasibility, and expected impact. |
| 08:15 | Creative Director approval | Approved, revise, or discard list | Human approval is required before external-facing delivery and should be required before paid image/3D generation during the pilot. |
| 09:00–14:00 | Image/3D production and deterministic compositing | Preview images, 3D scene previews, `.blend`, `.glb`, `.fbx`, and technical manifest as applicable | Per-tool caps, job retries, status logging, asset checksums, and output validation. |
| 15:00 | Quality Council | QC scorecard and remediation list | Brand, legal, cultural, typographic, file-spec, and brief-fit checks. |
| 16:00 | Client packager | A client-ready concept PDF/HTML, preview images, explanation, scope and assumptions; source/3D files only when within scope | Internal/Client/Archive access classification. |
| 17:30 | Portfolio and learning update | Approved internal showcase candidates, job metrics, errors, and verified outcome placeholders | Nothing publishes externally without client/project permission. |

## International-Grade Quality Standard

ZYNTH should adopt a single scorecard that applies across social, campaign, event, video, and 3D work. A passing output requires an average score of **4/5 or higher**, no score below **3/5**, and no mandatory-risk failure. The scorecard provides a common language for the strategist, design team, producer, and client.

| Dimension | What good looks like | Evidence required |
| --- | --- | --- |
| **Strategic relevance** | Work answers the stated business problem and audience tension, not a superficial production request. | Traceable link from objective → insight → proposition → CTA. |
| **Originality and distinctiveness** | The concept has a recognizable organizing idea and is not a generic festival greeting or trend imitation. | Novelty comparison against recent ZYNTH work and category references. |
| **Cultural intelligence** | Local occasion, language, representation, symbols, and sensitivities are accurate for the named market. | Verified cultural/source tag and regional reviewer sign-off for high-risk work. |
| **Brand coherence** | Work respects the approved brand platform, visual system, voice, logo, typography, and legal requirements. | Brand-kit version and checklist result. |
| **Craft and technical quality** | Layout, typography, resolution, motion/render quality, lighting, file formats, and packaging are professionally correct. | Deterministic technical QC plus Creative Director review. |
| **Feasibility and commercial discipline** | The concept fits the budget, production method, timeline, permits, and event/site constraints. | Cost range, scope assumptions, supplier/production feasibility check. |
| **Outcome orientation** | The creative approach has a measurable hypothesis and a defined measurement method. | Pre-set KPI, measurement owner, baseline/target where available, and post-launch data plan. |

## Campaign, Festival, and Industry Intelligence

A strong system must not try to create “all festivals for all industries” from memory. It needs a maintainable **Opportunity Graph** with source references, expiry dates, and explicit market contexts. The initial graph should cover Myanmar, Singapore, and any other ZYNTH priority market selected by management.

| Data layer | Key fields | Example use |
| --- | --- | --- |
| **Calendar and special occasions** | Occasion, date rule, country/region, observance type, source, cultural sensitivity, relevance window. | A festival activation is proposed only if culturally relevant and commercially appropriate for that brand. |
| **Industry moment map** | Industry, buying cycle, trade events, regulation/seasonality, audience behavior, channel context. | A B2B safety campaign is timed around factory planning, training, or compliance windows rather than a generic date. |
| **Brand and client knowledge** | Approved facts, audiences, products, competitors, market restrictions, assets, past work, objectives, approvals. | The system stops instead of inventing brand claims or a nonexistent product feature. |
| **Creative memory** | Concept territory, visuals, campaign logic, delivery date, performance, reviewer decisions, reuse restrictions. | Novelty checks prevent the same neon-poster or “festival greeting” treatment recurring across clients. |
| **Performance outcomes** | Objective, source system, measurement period, results, confidence, lesson candidate. | Promotes patterns only when verified performance evidence reaches the agreed threshold. |

## Client-Ready Deliverable Standard

Each approved concept should leave the system as a structured package that is easy to present, approve, produce, and archive.

| Package component | Image/campaign package | 3D/event package |
| --- | --- | --- |
| Strategic explanation | Business challenge, audience insight, concept rationale, message, CTA, applications, KPI hypothesis. | Event objective, guest journey, spatial narrative, zone/stage rationale, technical assumptions, KPI hypothesis. |
| Client preview | Key visual, channel adaptations, annotated layout, copy placeholder plan, usage examples. | Rendered hero views, annotated floor plan, camera views, material/palette board, guest-flow notes. |
| Production files | Approved source files, transparent/background variants, specification sheet, version log. | `.blend` master, `.glb` web/AR asset, `.fbx` vendor/interoperability asset, texture/asset manifest, render images. |
| Commercial clarity | Scope, included revisions, exclusions, recommended production route, indicative timeline. | Scope, scale/venue assumptions, build/fabrication exclusions, version notes, applicable vendor handoff requirements. |
| Approval evidence | Version, approver, date, comments, rights/usage status. | Version, approver, date, comments, source-model and asset-rights status. |

## Governance and Human Authority

ZYNTH should implement an AI governance register modeled on risk management, traceability, transparency, monitoring, and override principles.[5] [6] [7] Each agent run should record the task ID, data sources, prompt/specification version, model/tool version, reviewer, decision, asset outputs, and known limitations. The agency should tell clients when AI materially contributes to content or visual generation whenever that is contractually, legally, or ethically required.

| Decision class | Automation level | Human authority required |
| --- | --- | --- |
| Research, calendar extraction, internal opportunity scoring | Autonomous, evidence logged | Operations lead reviews low-confidence/high-risk items. |
| Concept drafting and proposal first drafts | Autonomous draft | Strategist/Creative Director approves client-facing recommendation. |
| Image/3D generation during pilot | Controlled automation | Creative Director approval; brand owner approval for new client work. |
| Public posting, paid-media launch, outbound client communication, contracts, pricing, vendor commitment | Never autonomous | Named authorized human only. |
| Learning promotion into standard prompts | Evidence-gated automation | Monthly governance review confirms verified evidence and removes outdated lessons. |

## Delivery Architecture Options

The decision is primarily about **where final creative generation runs**, not whether Zynth Brain can plan the work. Both options retain the current repository’s reliable planning, switches, approvals, queue, and learning capabilities.

| Approach | How it runs | Tradeoffs | Cost | Setup complexity |
| --- | --- | --- | --- | --- |
| **A. Controlled Creative Factory** | Zynth Brain automatically researches, plans, writes the three daily Concept Packages, produces proposal explanations, and queues image/3D jobs. A Creative Director triggers the approved jobs through the currently connected OpenArt and Blender environment. | Safest near-term approach; preserves strong review and cost controls. It does **not** deliver unattended 3D generation while the owner’s workstation/session is unavailable. | Uses the existing hosting and creative-tool subscriptions; generation only occurs after approval. | Low to medium. It extends the current queue, scorecard, and packager. |
| **B. Autonomous Production Runner** | Zynth Brain generates and approves job manifests; a dedicated always-on production machine runs Blender and the image provider integration on schedule, validates outputs, and returns packages to Zynth Brain. | Meets the full daily-production target, but requires reliable machine uptime, secure secrets, provider automation support, failure recovery, asset storage, and stricter operational monitoring. | Requires a continuously available machine and provider usage; exact cost depends on the existing OpenArt and Blender environment. | High. The current fixed Blender builder must be modularized, and the image provider must expose a supported automation route. |

## Recommended Implementation Sequence

The implementation should begin with a four-week pilot rather than immediately attempting every market, festival, industry, and media type. In Week 1, ZYNTH defines its priority markets, first six industry packs, first twenty occasions, verified brand templates, and quality rubric. In Week 2, the three-daily-brief factory, novelty guardrail, proposal explainer, and client-package generator are deployed. In Week 3, one image lane and one modular 3D event-scene lane are tested against the rubric with one internal brand and one willing client. In Week 4, the team measures approval rate, cycle time, rework rate, asset completion, client response, and early campaign signals before scaling.

The pilot should be considered successful only when the system produces at least three **reviewable Concept Packages** per working day, every released output carries a complete audit trail, no mandatory QC issue escapes to a client, and the team can identify which patterns merit further investment. Scale to unattended generation only after the generated work meets the quality scorecard consistently and the automation is proven in a non-client-critical environment.

## Immediate Decisions Required

The technical work can start once ZYNTH confirms the priority markets and industries, names the internal Creative Director/release authority, and chooses either the controlled or autonomous production approach. For the production-lane connection, the implementation also needs the supported OpenArt automation method, the location and runtime for Blender, and a secure method of configuring keys without committing them to Git.

## References

[1]: https://www.zynth.asia/ "ZYNTH — The Intelligence of Creativity"
[2]: https://github.com/zanezynthbrain/zynth-brain "Zynth Brain repository"
[3]: https://www.ana.net/content/show/id/pr-2024-09-warc "ANA and WARC: Building a culture of creative effectiveness"
[4]: https://ipa.co.uk/effworks/marketing-marketing-v2/creative-effectiveness-ladder "IPA: Creative Effectiveness Ladder"
[5]: https://www.iab.com/guidelines/cross-channel-measurement/ "IAB: Cross-Channel Measurement Best Practices"
[6]: https://www.nist.gov/itl/ai-risk-management-framework "NIST AI Risk Management Framework"
[7]: https://www.oecd.org/en/topics/sub-issues/ai-principles.html "OECD AI Principles"
[8]: https://www.iso.org/standard/42001 "ISO/IEC 42001: AI management systems"
