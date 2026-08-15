# 10 — AI AGENCY WORKFORCE SOP

**Owner:** Managing Director  
**Applies to:** Zynth Brain daily proposals, incoming project leads, creative queue, image production, 3D stage/spatial concepts, client-facing proposal preparation, and portfolio learning.  
**Version:** 1.0

## Purpose

Zynth Brain is an internal **AI workforce**, not an autonomous agency principal. Its purpose is to give ZYNTH a steady flow of commercially useful ideas and prepared proposal packages across industries, campaign types, events, sponsorships, content, video, and spatial design. It should save founder and team time in research, strategic drafting, concept development, proposal explanation, QC preparation, and asset packaging.

It must never convert an internal idea into a client promise, a published post, paid-media spend, supplier instruction, contractual commitment, or final deliverable without the appropriate human authority. The system is built to make ZYNTH faster and more consistent while retaining the judgment, cultural sensitivity, legal control, and client accountability that clients pay the agency for.

## The Two Workstreams

| Workstream | What it is | Automation level | Founder decision required? |
| --- | --- | --- | --- |
| **Daily Agency Workforce** | Three cross-sector internal Concept Packages created every day. Each package contains insight, concept, explanation, channel/application plan, delivery plan, KPI hypothesis, assumptions, risks, and production lane. | Automatic when the `autonomy` and `daily_workforce` switches are both on. | **No** to create internal drafts. **Yes** before connecting one to a real lead or production job. |
| **Real Lead / Client Project** | An actual inbound lead, client request, proposal opportunity, or delivery project. | Internal analysis and first drafts may be automated. | **Yes.** The project cannot progress to proposal, won, or delivery until the founder decision is recorded. |

> **The governing rule:** An AI-generated idea is internal intellectual work. A client project is a commercial commitment. The first can be automated; the second requires founder confirmation.

## Daily Concept Package Standard

A daily package is not an image alone. It must be strong enough for the founder to decide whether it is worth turning into a proposal, creative territory, pitch, or internal showcase.

| Required section | Standard |
| --- | --- |
| Opportunity | The commercial, seasonal, cultural, industry, audience, or business moment being addressed. It must be stated as an opportunity, not an invented fact. |
| Objective and audience | A real business objective and defined audience; never “everyone.” |
| Human insight | A tension, behavior, motivation, or barrier that explains why the idea could matter. |
| Proposition and concept | One single-minded proposition and one distinctive organizing idea. The concept should not be a generic festival greeting or visual trend. |
| Activation system | At least three connected actions or experiences that show how the idea lives beyond a single key visual. |
| Channels and deliverables | Clear role for each channel and a defined set of outputs. A full omnichannel concept must explain how channels connect rather than list platforms. |
| Outcome hypothesis | Measurable KPI hypotheses and the future source of measurement. Hypotheses are not performance promises. |
| Creative direction | Art direction, production lane, and limitations. Typography, logos, and legal text are composed after review—not generated blindly. |
| Client explanation | A concise story that explains why the proposal is relevant, distinctive, and commercially useful. |
| Assumptions, questions, and risks | These are mandatory. The system must not hide missing brand facts, cultural verification needs, venue/build assumptions, budget uncertainty, or legal questions. |

## Daily Coverage Rotation

The daily workforce rotates through the following work lanes. It assigns exactly three distinct lanes each day and alternates Myanmar and Singapore industries, so the output does not become repetitive or limited to social-post ideas.

| Work lane | Typical ZYNTH output |
| --- | --- |
| Integrated Campaign | Brand platform, launch, awareness, behavior change, customer acquisition, or category-growth idea. |
| Sponsorship Programme | Sponsorship platform, entitlement logic, experience design, brand value story, and measurement framework. |
| Digital / Omnichannel | Connected paid, owned, social, CRM, website, and experience journey with channel roles. |
| Social / TikTok Challenge | Participation mechanics, creator behavior, safe rules, short-form narrative, and moderation considerations. |
| Corporate Event | Conference, awards, launch, internal culture, leadership, or customer event with guest journey and production assumptions. |
| Stage / Spatial Experience | Stage, exhibition, activation, or event-environment concept that can later enter the Blender production lane. |
| Video Storyboard | Film proposition, story structure, shot direction, sample-frame plan, and production assumptions. |
| Seasonal / Cultural Activation | Locally appropriate special-day or festival idea that earns brand relevance rather than copying an occasion. |

The default industry rotation covers finance, property, F&B, retail/e-commerce, healthcare, education, manufacturing/industrial, tourism/hospitality/MICE, technology, beauty/wellness, media/content, automotive/mobility, logistics/supply chain, public sector, and related verticals. The calendar is a prompt for opportunity exploration; a concept is released only after the relevant local cultural and brand context is verified.

## Founder Approval Gates

### Gate A — Daily Draft Review

The daily worker may create three internal packages and notify the founder. Each package begins with the following immutable operating state:

| Field | Initial value |
| --- | --- |
| Status | `internal_draft` |
| Founder decision | `founder_review_required` |
| Client contact | Disabled |
| Production | Disabled |
| Publishing | Disabled |

The founder can archive a package, request a revision, assign it to an approved project, or hold it as reusable intellectual property. A package is not a client proposal merely because it is polished.

### Gate B — Real Lead / Project Confirmation

An imported or agent-discovered project record enters the pipeline with `founder_approval = pending`. It cannot move to **proposal**, **won**, or **delivery** until the founder records **approved**. A declined record remains as an audit trail and cannot progress.

| Decision | Meaning | Permitted next action |
| --- | --- | --- |
| Pending | Lead or project exists but is not authorized for commercial action. | Research and internal draft only. |
| Approved | Founder has decided that ZYNTH should pursue or execute the work. | Proposal preparation, selected production authorization, and internally managed delivery tasks. |
| Declined | Not strategically suitable or not ready. | Archive, future follow-up only if the founder explicitly reopens it. |
| Not required | Founder directly created an internal/owned project. | Work according to normal delivery gates. |

### Gate C — Creative Production Authorization

A founder-approved daily package can enter the creative queue only when it is linked to a founder-approved project. The queue records the package ID, project ID, founder name, time, automation mode, template ID where applicable, and decision note.

| Production route | Current rule |
| --- | --- |
| **Founder-triggered image** | Allowed after Gate B and Gate C. Generate one controlled preview, then run QC. |
| **Template-auto image** | Allowed only for a pre-approved image template, a declared template ID, an approved project, and a defined output limit. This is for low-risk variation—not for original client campaign territory. |
| **3D / Blender scene** | Founder-triggered only. A live output needs review for spatial feasibility, scale, materials, brand fit, venue constraints, and file integrity before client use. |
| **Video / sample motion** | Briefs and storyboards can be prepared automatically. Actual generation remains founder-triggered until the provider connection, rights, and review process are verified. |
| **Publishing or paid media** | Never approved by the daily workflow. Use the separate review and release process. |

## Founder Daily Operating Rhythm

| Time | Founder action | Workforce action |
| --- | --- | --- |
| 09:30 Yangon | Review the Telegram notification or run `/workforce` on demand. | Creates three cross-sector Concept Packages and saves them to the internal workforce archive. |
| 09:45–10:00 | Mark each package: archive, revise, keep as IP, or attach to a real approved project. | Holds all packages in internal-only status. |
| During a live lead/project | Confirm the project once it is strategically valid. | Uses the approved project and internal package to develop a fuller proposal or selected production job. |
| Before asset generation | Choose founder-triggered preview, or template-auto image where the client/template qualifies. | Creates an auditable creative-queue job only after Gate C. |
| Before sending to client | Review strategy, brand, copy, technical output, legal statements, and scope. | Prepares the client package and QC evidence. |
| Friday | Review what was approved, rejected, used, repeated, and converted into real opportunities. | Produces activity/quality evidence for the operating review. |

## Quality Control Before Client Use

Every concept, image, 3D render, storyboard, or proposal must pass the existing three-gate ZYNTH Quality System and the following AI-specific checks.

| Check | Reviewer / evidence |
| --- | --- |
| Brief fit, business objective, and single-minded proposition | Strategist or founder. |
| Distinctiveness and category relevance | Creative Director/founder; compare against recent ZYNTH work and known competitor patterns. |
| Cultural context and representations | Relevant market reviewer for sensitive occasions, religious/cultural signals, language, or community claims. |
| Brand system, logo, typography, legal copy, claims, and accessibility | Brand owner/Creative Director; use the current verified brand kit. |
| Technical integrity | Correct dimensions, resolution, color profile, source files, filenames, 3D exports, and preview renders. |
| Commercial feasibility | Producer/founder confirms budget, scope, timeline, vendor/venue assumption, and revision policy. |
| Outcome measurement | A named owner, baseline/target where available, data source, and reporting date. |

## OpenArt and Blender Operating Requirement

The current Zynth Brain codebase can prepare prompts and has a Blender scene-builder that exports `.blend`, `.glb`, and `.fbx`; its present image-rendering module is configured for OpenAI Images. Before OpenArt becomes an automatic production lane, ZYNTH must document the supported connection method, provider terms, model/version, output ownership, daily cap, retry behavior, and media-storage location. No secret belongs in Git.

The current Blender script is a valuable proof of output but should be treated as a starting scene kit rather than a universal 3D agent. The next production milestone is to create modular and parameterized scene kits for the highest-value event types: conference/summit, gala/awards, product launch, exhibition/booth, retail activation, and corporate town hall. Each kit should require venue dimensions, guest capacity, stage program, brand palette, technical rider, and material/build assumptions before finalizing.

## Metrics and Monthly Governance

The system is working only if it improves real agency throughput and decision quality. Review the following monthly.

| Metric | Definition | Target behavior |
| --- | --- | --- |
| Daily package completion | Days with three complete internal Concept Packages. | High consistency without sacrificing QA. |
| Founder acceptance rate | Packages kept, revised, or attached to projects ÷ packages reviewed. | Improves over time; low acceptance exposes poor brief or repetition quality. |
| Time to proposal | Time from approved real lead to client-ready proposal. | Reduces while preserving commercial and craft review. |
| Production rework rate | Jobs returned from QC ÷ jobs generated. | Declines as templates, brand kits, and prompts improve. |
| Client approval rate | First/second-round approvals ÷ client presentations. | Improves through stronger briefing and quality control. |
| Outcome evidence coverage | Completed projects with verified KPI source and post-project report. | Reaches 100%; no unsupported success claims. |
| Learning quality | Lessons promoted only from repeated, verified outcomes. | Prevents the system from learning from unverified model opinions. |

## Activation Checklist

The new daily workforce ships **off by default**. This prevents automated API usage before the founder is ready.

1. Confirm that the live AI credential is configured in the deployed environment; mock mode intentionally produces no daily workforce output.
2. From Telegram, use `/switch daily_workforce on`, then `/active` when the master autonomous mode is ready. Keep all other autonomous switches under separate control.
3. Test `/workforce` once and review the saved package before enabling the schedule.
4. Confirm the production environment for OpenArt and Blender, then document the approved image templates and 3D scene kits.
5. Start with a two-week internal pilot. Do not send automated concepts to clients; score the work, revise the prompt/library, and only then attach selected packages to live approved projects.

> **Non-negotiable:** The system may proactively create excellent internal work. Only the founder authorizes ZYNTH to make a real-world promise.
