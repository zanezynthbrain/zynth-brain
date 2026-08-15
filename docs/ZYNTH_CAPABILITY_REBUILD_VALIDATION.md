# ZYNTH Capability Rebuild Validation

**Date:** 15 August 2026  
**Scope:** Skills, agents, runtime specifications, Vault/Drive role cards, SOP-facing knowledge, quality controls, and approval boundaries in `zanezynthbrain/zynth-brain`.

## Executive Conclusion

The original concern was valid. The repository contained valuable operating IP, particularly in the master planners and deep specialist reference libraries, but the system presented unevenly. Some entry-point skills and Drive-facing role cards were too compact to function as complete, professional operating systems on their own. The public-facing symptom was a generic one-page role/skill view that obscured richer material elsewhere in the repository.

The rebuild establishes a single agency-wide operating contract and applies it to every current skill. It materially deepens the priority capabilities most central to ZYNTH’s daily creative workforce and commercial engine: 3D/design, video, sponsorship, prospect intelligence, offer construction, objections, pitch packages, and copy. It adds individual operating specifications for active leadership and specialist agents, upgrades the Drive/Vault role-card layer, and fixes the mirror that previously showed folded YAML descriptions as `>` instead of meaningful capability summaries.

> **This is now a governed capability system, not a loose library of prompts.** It can produce ambitious internal work autonomously while retaining founder approval for real projects, client communication, commitments, spend, publication, and final release.

## What Changed

| Layer | Completed change | Evidence |
| --- | --- | --- |
| **Universal agency standard** | Created a single Capability System Standard covering work bands, preflight, evidence, three-territory creative development, commercial logic, quality gates, governance, handoffs, role architecture, and learning. | `docs/ZYNTH_CAPABILITY_SYSTEM_STANDARD.md` |
| **All skills** | Applied the shared operating-contract pointer to **36/36** current skill entry points. | `.claude/skills/*/SKILL.md` |
| **Priority creative production** | Rebuilt the 3D Design Studio and Commercial Video Studio with complete production workflows, source-file/rights/QC rules, output packages, templates, and approval gates. | `zynth-3d-design-studio`, `zynth-commercial-video-studio` |
| **Creative quality** | Added a structured creative route, evidence/claim, localisation, testing, output-package and QA layer to the Copywriter capability. | `zynth-copywriter` |
| **Commercial engine** | Rebuilt ICP, objection, offer, sponsorship, and pitch skills around evidence, scope, finance validation, commercial trade-offs, proof, fulfilment and founder decision rules. | `zb-icp`, `zb-objections`, `zb-offer`, `zb-pitch-kit`, `zynth-sponsorship-value` |
| **Agent system** | Added **13** new runtime operating specifications, raising active agent specs to **25**. The BaseAgent now injects universal evidence, creativity, feasibility, quality, and approval controls into every specialist prompt. | `backend/agents/specs/`; `backend/agents/base.py` |
| **Drive/Vault usability** | Corrected multi-line skill-description parsing; every Skill Index entry now exposes the full repo path and resource count. Added mirrors for the Capability Standard and Rebuild Architecture. | `backend/utils/obsidian.py`; `vault/ZYNTH-OS/Skills Index.md` |
| **Role cards** | Upgraded **12** Drive-facing JDs with mission, inputs, outputs, cadence, decision rights, escalation, quality/handoff and full-source routes. | `vault/ZYNTH-OS/Roles/` |
| **Repeatability** | Added the operating-asset audit, all-skill standard migration, missing-agent spec generator, role-charter upgrade, Vault mirror refresh, and formatting cleanup utilities. | `scripts/` |

## New Capability Standard

The system now requires every material capability to make the following clear before it is treated as client-ready:

| Control | Required behaviour |
| --- | --- |
| **Work band** | Classify activity as Explore, Propose, Execute, or Release. No silent step from internal draft to external commitment. |
| **Evidence** | Label confirmed facts, observed signals, hypotheses, and unknowns. Do not invent clients, budgets, vendors, claims, results, contacts, permissions, or timelines. |
| **Creative excellence** | Develop three genuinely distinct territories for material creative work before recommending a selected route. |
| **Execution** | Convert an idea into owners, deliverables, dependencies, timing, production method, risks, measurement and handoff. |
| **Commercial integrity** | Expose scope, resource/cost assumptions, funding/margin logic, terms and trade-offs; request finance validation where appropriate. |
| **Quality** | Use a 1–5 cross-functional quality gate; material work needs 4+ in every applicable category and 4.2+ average. |
| **Approval** | Founder/project-owner approval remains mandatory for real leads/projects, client communication, spend, vendor commitment, publication, contracts, paid-media change and final release. |
| **Learning** | Preserve decision, evidence, quality score, feedback, performance/variance and reusable verified lesson. |

## Validation Results

| Validation | Result | Interpretation |
| --- | --- | --- |
| Focused regression: Vault mirror + shared agent contract | **16 passed** | The corrected Drive-facing index and universal specialist-prompt controls are covered. |
| Full Zynth Brain regression suite | **265 passed; 1 failed** | The only failure is the existing environment-dependent Graphify check: it expects a missing `graph.json` detail even when the Graphify package itself is unavailable. This failure occurred before this rebuild and is unrelated to the capability changes. |
| Formatting and merge safety | **Passed** | `git diff --check` is clean. |
| New script syntax | **Passed** | All new/modified rebuild utility scripts compile with `py_compile`. |
| Skill operating-contract coverage | **36/36** | Every current skill has the common ZYNTH operating-contract link. |
| Runtime-agent specification coverage | **25 specs** | All currently identified runtime specialist keys now have a role-specific operating spec or an existing deep spec. |
| Vault mirrors | **Passed** | The Capability Standard and Rebuild Architecture are mirrored in `vault/ZYNTH-OS`; the Skills Index shows full sources and no longer reduces folded descriptions to `>`. |
| Post-rebuild skill audit | **0 rebuild-priority, 9 needs-strengthening, 27 strong-base** | The remaining nine are not generic/uncontrolled; they inherit the common standard but need dedicated reference/template expansion to become the next priority wave. |

## Remaining Hardening Wave

The following capabilities are now governed by the universal standard but should receive the same deep reference/template treatment in the next conversion wave. They are ordered by agency leverage, not by a claim that they are unusable today.

| Priority | Capability | Next rebuild focus |
| --- | --- | --- |
| **1** | `zynth-art-director`, `zynth-creative-director`, `zynth-tactical-prompts` | Creative territory system, creative briefing, craft reviews, prompt/reference library, originality/cultural/rights checks and evaluation examples. |
| **2** | `zynth-event-manager` | Integrated supplier/RFQ, run-of-show, safety/permit, budget/contingency, site/crew and closeout templates that link to the Master Event Planner. |
| **3** | `zynth-paid-media-specialist`, `zynth-analytics-specialist` | Measurement dictionary, tracking-validation, test register, data-quality diagnostics, reporting/decision template and media-change approval flow. |
| **4** | `zynth-bd-researcher`, `zynth-competitor-analyst`, `zynth-seo-specialist` | Source protocols, research schemas, evidence-confidence levels, decision templates and current-data refresh rules. |

## Founder Operating Routine

To make the new system powerful in practice, retain a short founder rhythm rather than trying to personally create every item.

| Cadence | Founder decision |
| --- | --- |
| **Daily** | Review the three internal opportunity/concept packages; select, defer, request refinement, or archive. Approve any real lead/project movement. |
| **Weekly** | Review pipeline priority, proposal/pitch readiness, creative/3D/video QA, project risk/margin, calendar gaps and production queue. |
| **Monthly** | Review wins/losses, delivery variance, QC/revision causes, client feedback, performance evidence, capability gaps and templates to promote. |
| **Quarterly** | Revalidate industries/markets, agency offers, rate/vendor knowledge, role capacity, approval limits, and the next skills to harden. |

## Handover Materials

The primary documents for using and extending the system are:

1. `docs/ZYNTH_CAPABILITY_SYSTEM_STANDARD.md` — mandatory agency operating contract.
2. `docs/ZYNTH_SKILL_REBUILD_ARCHITECTURE.md` — target architecture and rebuild pattern.
3. `docs/ZYNTH_OPERATING_ASSET_AUDIT.md` — reproducible scorecard and next-priority list.
4. `docs/playbook/10_AI_Agency_Workforce_SOP.md` — daily AI workforce and founder-control process.
5. `vault/ZYNTH-OS/Skills Index.md` — readable capability directory, now linked to complete source paths.

The implementation is intentionally founder-controlled. It makes agents proactive, rigorous, creative, and result-oriented, but it does not allow them to impersonate you, send work externally, promise outcomes, spend funds, commit suppliers, or take ownership of client relationships without your decision.
