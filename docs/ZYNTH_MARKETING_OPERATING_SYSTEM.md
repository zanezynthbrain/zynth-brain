# ZYNTH Marketing Operating System

## Purpose

This repository documents the **no-cost-first** operating system for generating, reviewing, learning from and managing Myanmar-first marketing campaigns, event/exhibition activations and standalone commercial/storyboard work. The live portfolio source of truth is the Google Sheet below. This repository is the technical-change, version-control and issue-board fallback location.

> **No paid API is required for the base workflow.** Do not introduce paid API keys, paid automation, a server, a new subscription, or an external action without a separately recorded human approval.

## Canonical Live System

| Asset | Purpose | Link |
|---|---|---|
| ZYNTH Master Tracker | Current campaign, commercial, research, AI Council, approvals and learning records | [Open live tracker](https://docs.google.com/spreadsheets/d/1lJd6DkGcKrCAiETw9qadftFZhc-uXDNBr8Q1JlHLqMo/edit) |
| Dashboard | The live tracker **Overview** tab is the no-cost Command Center dashboard; it includes campaign budget, scenario contribution and ROI charts | [Open Overview](https://docs.google.com/spreadsheets/d/1lJd6DkGcKrCAiETw9qadftFZhc-uXDNBr8Q1JlHLqMo/edit#gid=906936946) |
| Intake & Decision Form | Registers a proposal, AI Council contribution, source, approval or task for human review | [Open form](https://docs.google.com/forms/d/e/1FAIpQLSeBxa-bcTauFyceX2V9FwFh5bNVd20vf9q3ponUnMDnXUpRBA/viewform) |
| Drive operating-system folder | Holds the permanent user-owned operating-system assets | [Open Drive folder](https://drive.google.com/drive/folders/1DQkkmigtyZodDOybu1i1Mtwe8EtFIGBw) |
| Technical issue-board fallback | Tracks build improvements, decision gates and operating work when GitHub Projects is unavailable | [Open ZYNTH issues](https://github.com/zanezynthbrain/zynth-brain/issues?q=is%3Aissue%20is%3Aopen%20label%3Azynth-system) |

## The Two Independent Creative Tracks

| Track | Stable ID format | Required record | Current rule |
|---|---|---|---|
| Campaign / activation | `CMP-YYYY-INDUSTRY-###` | Commercial tension, audience/behaviour, conversion mechanism, creative territory, G0–G7 gate, budget scenario, KPI and asset links | One campaign concept per row. Do not create a new workbook for each batch. |
| Standalone commercial / storyboard | `COM-YYYY-INDUSTRY-###` | Proposition, logline, visual style, detailed storyboard status, rights/claims, production feasibility, master/cutdown plan and asset links | A commercial can link to a campaign but remains separately numbered and separately governed. |

## Current Technical Board

GitHub Projects creation was attempted but the available GitHub token lacks the required `project` permission. Until that scope is approved, the open issues below are the live repository board.

| Issue | Workstream | Purpose |
|---|---|---|
| [#37](https://github.com/zanezynthbrain/zynth-brain/issues/37) | Campaign & Activation | Repeatable G0–G7 operating loop and next ten campaign records. |
| [#38](https://github.com/zanezynthbrain/zynth-brain/issues/38) | Commercial Studio | Independent commercial/storyboard pipeline and detailed 12-frame requirement. |
| [#39](https://github.com/zanezynthbrain/zynth-brain/issues/39) | Evidence & Risk | Claim-level evidence, limitations, proposed/TBC and red-team review. |
| [#40](https://github.com/zanezynthbrain/zynth-brain/issues/40) | Tracker & Dashboard | Live tracker and command-center maintenance. |
| [#41](https://github.com/zanezynthbrain/zynth-brain/issues/41) | AI Council | Manual, provider-neutral specialist/critic/human-resolution workflow. |
| [#42](https://github.com/zanezynthbrain/zynth-brain/issues/42) | Learning Library | Closed-work learning and weekly review routine. |

## Manual AI Council — No API Required

1. Create one canonical brief in the **AI Council** tab.
2. Paste the same factual brief into an available AI web interface. Do not send confidential information, personal data, passwords, contracts or unapproved commercial rates.
3. Assign one defined role: **Research**, **Strategy**, **Creative**, **Production**, or **Critic/Red Team**.
4. Record the concise structured output, source/evidence links, strengths, weaknesses and contradiction flags in the tracker. Do not store large unstructured chat transcripts as the portfolio record.
5. A human owner records **Accept**, **Revise**, **Hold** or **Reject**, the reason, the risk owner and the next gate.

The system is provider-neutral. Manus can orchestrate and produce integrated proposals; another available AI may provide a bounded research, critique or technical contribution. The human decision record—not the model output—is the authority.

## Mandatory Quality Gates

| Gate | Human question |
|---|---|
| G0 — Brief Accepted | Is the objective, client boundary, budget band, required outcome and owner clear? |
| G1 — Research Cleared | Are factual claims sourced, limited and distinguished from assumptions? |
| G2 — Strategy Selected | Is there a credible behavioural/conversion mechanism and measurement plan? |
| G3 — Creative Selected | Is the creative territory materially distinct, culturally appropriate and clear? |
| G4 — Feasibility Cleared | Are production, access, rights, privacy, safety, technical and budget risks addressed? |
| G5 — Go / No-go | Has the named human owner approved the correct final artifact? |
| G6 — Live Optimisation | Are delivery signals and customer/participant safeguards monitored? |
| G7 — Learn & Archive | What worked, did not work, changed, and should be re-used next time? |

## Weekly Learning Ritual

Each week, read the **Learning & Guide** sheet and answer the ten review questions for every selected or closed record. Label the outcome `Proven`, `Promising`, `Unproven` or `Do not reuse`. Link the resulting learning note back to its `CMP` or `COM` ID and create/update the related GitHub issue if the operating system itself needs improvement.

## Upgrade Rule

Stay manual and no-cost-first until the team has completed **three to five successful cycles** and can name a measured, repetitive bottleneck. Only then compare a scoped upgrade. Any upgrade proposal must state the cost owner, provider, data boundary, expected benefit, rollback approach and explicit approval record.
