# ZYNTH Skill, Agent, and Knowledge Rebuild Architecture

**Decision:** Retain the existing strong master planners and deep capability files, then rebuild the weak entry-point skills, standardise every operating contract, expand per-agent specifications, and repair the Vault/Drive presentation layer.

## Audit Conclusion

The repository is not empty or uniformly generic. It contains a useful foundation: the master campaign, event, and proposal planners are compact navigation files supported by detailed reference libraries; the content studio is a substantial engineered workflow; the wider playbook is materially more complete than the Drive role cards suggest. The problem is structural inconsistency.

The current library mixes deep systems with one-page promises. Several short skills claim an “end-to-end” capability but do not visibly state a qualification contract, decision method, output contract, QA rubric, or commercial/approval boundary. The Drive/Vault role cards intentionally compress richer material into 27–28 lines, but they fail to link a reader to the full method. The skill index also reads only the first line of folded YAML descriptions, causing many rich skills to appear as `>`.

> **The rebuild objective is not to make every `SKILL.md` long. It is to make every capability executable, navigable, evidence-aware, commercially disciplined, and quality-controlled.**

## Target Architecture

| Layer | Purpose | Source of truth | Required rule |
| --- | --- | --- | --- |
| **Capability entry point** | Select the right skill and run the core method. | `.claude/skills/<skill>/SKILL.md` | Under 500 lines; includes all nine Universal Capability Contract elements or routes precisely to the relevant resource. |
| **Method library** | Give specialised steps, checklists, rubrics, examples, sector variants, and decision rules. | `references/` | Read only when task type requires it; facts/rates are dated. |
| **Production resources** | Ensure consistent artefacts or deterministic operations. | `templates/`, `scripts/` | Validate any script; do not embed secrets. |
| **Agent operating spec** | Inject mandate, inputs, outputs, handoffs, decision rules, and quality threshold into the running agent. | `backend/agents/specs/<agent>.md` | Required for every active specialist agent. |
| **Knowledge/data source** | Store verified market facts, client facts, rates, vendors, and lessons separately. | `backend/knowledge/`, project files | Date, source, owner, and verification status are mandatory. |
| **Human-facing manual** | Allow the founder and human staff to understand/operate the system. | `docs/` mirrored to `vault/ZYNTH-OS/` | Link to full source capability, not merely a summary card. |

## Priority Portfolio

| Priority | Capability set | Current issue | Rebuild action |
| --- | --- | --- | --- |
| **P0 — universal** | All skills and agents | No single shared contract for qualification, evidence, quality, approvals, commercial feasibility, and learning. | Apply the Capability System Standard; inject the essential operating rules into the shared BaseAgent prompt; mirror the standard. |
| **P0 — Drive/Vault** | Skills Index and role cards | Folded YAML descriptions become `>`; compact cards look like the entire JD/skill. | Parse multiline YAML descriptions; add source links, capability level, and full-manual routes. |
| **P1 — commercial intelligence** | `zb-icp`, `zb-objections`, `zb-offer`, `zb-pitch-kit`, `zynth-sponsorship-value` | Broad claims with fragmented/no visible input, output, value, proof, and approval contracts. | Rebuild as linked BD-to-proposal-to-sponsorship system, with decision templates and proof/rights guardrails. |
| **P1 — creative production** | `zynth-3d-design-studio`, `zynth-3d-production`, `zynth-commercial-video-studio`, `zynth-video-producer`, `zynth-copywriter`, `zynth-tactical-prompts` | Tools and styles are named, but production handoffs, media QC, output packages, rights, buildability, and reusable templates are uneven. | Introduce end-to-end production standards, complete packages, QA scorecards, and low-risk automation lanes. |
| **P1 — delivery excellence** | `zynth-event-manager`, `zynth-project-manager`, `zynth-account-manager`, `zynth-analytics-specialist` | Strong material exists but handoff, evidence, and operating-state contracts vary. | Standardise intake, RACI, change control, client review, outcome reporting, and closeout. |
| **P2 — growth performance** | `zynth-paid-media-specialist`, `zynth-seo-specialist`, `zynth-social-media-manager`, `zynth-content-strategist`, research/competitor skills | Good tactical knowledge but limited cross-channel experimentation and evidence lifecycle. | Add test registers, measurement dictionary, decision cadence, source protocol, and campaign learning loop. |
| **P2 — agent depth** | CEO/CMO/COO/CFO/HR, copywriter, event manager, operations, paid ads, research/SEO, roundtable, lead gen | Only 12 specialist operating specs exist; several active agents rely mostly on compact code role prompts. | Add/update specs, schemas, and focused tests; use the shared contract instead of duplicating long prompts. |

## Standard Rebuild Pattern

Every updated skill will follow this structure.

1. **Frontmatter:** A precise trigger, scope, market applicability, and non-overlap with sister skills.
2. **Mission and work band:** Define whether the skill may Explore, Propose, Execute, or Release.
3. **Preflight:** State mandatory inputs, default assumptions, and clarification limit.
4. **Method:** Use ordered workflow plus conditional branches.
5. **Methods/resources:** Link to detailed sector, production, budget, rights, or template resources as needed.
6. **Output contract:** Specify the finished package, data schema/table, files, and labels.
7. **Quality gate:** State scorecard, pass threshold, self-review, and revision actions.
8. **Governance:** State evidence labels, commercial rules, human approval, cultural/rights safety, and handoff.
9. **Learning:** State what evidence to store and when a reusable lesson is promoted.

## Acceptance Tests

A rebuilt capability is accepted only when the following are true.

| Test | Evidence |
| --- | --- |
| Correct selection | A user can tell when to invoke this skill and when to use another one. |
| Brief completeness | Missing critical information results in questions or labelled assumptions, never fabricated facts. |
| Creativity quality | Material creative work contains three genuinely distinct territories and a selection rationale. |
| Execution readiness | The output maps decisions to owners, deliverables, timing, resources, risks, and dependencies. |
| Commercial discipline | A quote/proposal identifies scope, budget/price assumptions, margin/funding logic, and approval state. |
| Measurement integrity | Every outcome claim has a source; every KPI has a decision use, owner, and review date. |
| Safe automation | Internal drafts cannot trigger external release, spend, contract, or sensitive production without approval. |
| Mirror usability | Drive/Vault displays the full source route and never implies a short card is the whole system. |

## Delivery Sequence

The initial implementation will fix the Drive-visible mirror problem and introduce global standards first. It will then fully rebuild the P1 commercial and creative-production entry points, expand the agent operating-spec coverage, and provide a reusable Role Charter system. The P2 specialisms will inherit the same standard and be converted in priority order using the portfolio scorecard, rather than copying generic text into every file.

## References

The universal brief contract reflects established professional guidance that successful creative briefs explicitly establish objectives, audience, message, deliverables, timeline, budget, stakeholders, and a review cycle.[1] [2]

[1]: https://business.adobe.com/blog/basics/creative-brief "Adobe: The creative brief — everything you need to know"
[2]: https://www.bynder.com/en/blog/find-creative-direction-write-great-creative-brief/ "Bynder: Writing an effective creative brief"
