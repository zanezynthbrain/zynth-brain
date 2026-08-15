# ZYNTH Operating Asset Audit

## Method

This static review tests whether each skill exposes the minimum operating contract required for repeatable agency work: a clear trigger, qualification/brief, workflow, output, quality gate, guardrails, commercial or outcome discipline, supporting references, and adequate depth. It is a **gap detector**, not evidence that the underlying advice is true; rates, laws, vendors, market facts, and client claims must still be verified at the point of use.

**Skills assessed:** 36. **Rebuild priority:** 0. **Needs strengthening:** 9. **Strong base:** 27.

## Skill Scorecard

| Skill | Lines | Refs | Scripts | Score | Status | Missing operating controls |
|---|---:|---:|---:|---:|---|---|
| `graphify` | 707 | 8 | 0 | 9/9 | Strong base | — |
| `yadana-finance` | 133 | 0 | 0 | 8/9 | Strong base | references |
| `zb-icp` | 97 | 1 | 0 | 9/9 | Strong base | — |
| `zb-objections` | 68 | 1 | 0 | 9/9 | Strong base | — |
| `zb-offer` | 87 | 0 | 0 | 9/9 | Strong base | — |
| `zb-pitch-kit` | 78 | 0 | 0 | 9/9 | Strong base | — |
| `zynth-3d-design-studio` | 129 | 1 | 0 | 9/9 | Strong base | — |
| `zynth-3d-production` | 62 | 5 | 0 | 8/9 | Strong base | workflow |
| `zynth-account-manager` | 373 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-analytics-specialist` | 271 | 0 | 0 | 7/9 | Needs strengthening | brief, references |
| `zynth-art-director` | 275 | 0 | 0 | 6/9 | Needs strengthening | workflow, commercial, references |
| `zynth-bd-pitch-prep` | 314 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-bd-researcher` | 213 | 0 | 0 | 7/9 | Needs strengthening | workflow, references |
| `zynth-brand-strategist` | 156 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-campaign-planner` | 190 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-campaign-requirements` | 314 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-commercial-video-studio` | 127 | 1 | 0 | 9/9 | Strong base | — |
| `zynth-competitor-analyst` | 299 | 0 | 0 | 7/9 | Needs strengthening | workflow, references |
| `zynth-content-strategist` | 259 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-copywriter` | 250 | 1 | 0 | 9/9 | Strong base | — |
| `zynth-creative-director` | 207 | 0 | 0 | 7/9 | Needs strengthening | workflow, references |
| `zynth-creative-video-director` | 127 | 9 | 0 | 9/9 | Strong base | — |
| `zynth-event-manager` | 154 | 0 | 0 | 7/9 | Needs strengthening | workflow, references |
| `zynth-market-researcher` | 200 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-master-campaign-planner` | 81 | 4 | 0 | 9/9 | Strong base | — |
| `zynth-master-event-planner` | 83 | 4 | 0 | 9/9 | Strong base | — |
| `zynth-master-proposal-writer` | 75 | 2 | 0 | 9/9 | Strong base | — |
| `zynth-paid-media-specialist` | 280 | 0 | 0 | 7/9 | Needs strengthening | brief, references |
| `zynth-pitch-packager` | 355 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-project-manager` | 322 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-seo-specialist` | 253 | 0 | 0 | 7/9 | Needs strengthening | commercial, references |
| `zynth-social-media-manager` | 207 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-sponsorship-value` | 116 | 6 | 0 | 9/9 | Strong base | — |
| `zynth-tactical-prompts` | 53 | 7 | 0 | 7/9 | Needs strengthening | brief, depth |
| `zynth-vendor-finder` | 418 | 0 | 0 | 8/9 | Strong base | references |
| `zynth-video-producer` | 148 | 0 | 0 | 8/9 | Strong base | references |

## Agent Architecture Scorecard

This scorecard reviews implementation affordances, not the strategic quality of the prompts or skills each agent may call.

| Agent | Lines | Score | Missing engineering controls |
|---|---:|---:|---|
| `base` | 135 | 4/5 | tests |
| `ceo` | 331 | 4/5 | tests |
| `cfo` | 88 | 2/5 | quality, error-control, tests |
| `cmo` | 92 | 2/5 | quality, error-control, tests |
| `content_studio` | 1466 | 5/5 | — |
| `coo` | 66 | 2/5 | quality, error-control, tests |
| `copywriter` | 93 | 2/5 | quality, error-control, tests |
| `critic` | 102 | 4/5 | tests |
| `event_manager` | 109 | 2/5 | quality, error-control, tests |
| `event_team` | 261 | 3/5 | error-control, tests |
| `hr` | 100 | 2/5 | quality, error-control, tests |
| `improver` | 170 | 4/5 | tests |
| `lead_gen` | 158 | 2/5 | quality, error-control, tests |
| `market_researcher` | 134 | 4/5 | tests |
| `master_proposal` | 201 | 4/5 | tests |
| `operations` | 124 | 2/5 | quality, error-control, tests |
| `orchestrator` | 302 | 5/5 | — |
| `paid_ads` | 147 | 2/5 | quality, error-control, tests |
| `portfolio` | 148 | 4/5 | tests |
| `proposal_factory` | 287 | 4/5 | tests |
| `research_seo` | 97 | 2/5 | quality, error-control, tests |
| `roundtable` | 108 | 2/5 | base-agent, schema, tests |
| `video_team` | 268 | 4/5 | tests |

## Priority Interpretation

A short skill is not automatically poor. It becomes an implementation risk when it offers a broad promise such as ‘deliver end to end’ but lacks concrete inputs, output contract, process, quality gate, safeguards, and references. Rebuild-priority skills should become concise navigation files with the detailed methods, templates, schemas, and rate/market references stored in their own `references/`, `templates/`, and `scripts/` folders.
