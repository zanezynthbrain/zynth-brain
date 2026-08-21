# ZYNTH Zero-Cost-First Architecture Decision

## Decision

Adopt a **Google Sheets Master Tracker + Google Drive asset library + Looker Studio dashboard + GitHub Projects technical board + manual structured AI Council** as the first ZYNTH operating system.

This choice is deliberately **API-free**. It continues the current proposal-production approach while replacing disconnected deliverables with a living master record. It does not require a paid AI API, an always-on server, a paid automation service or a custom web application.

## Why This Option Wins

| Decision criterion | Google-first stack | Airtable Free | Notion Free | Local-only/Obsidian + Ollama | Custom multi-AI application |
|---|---|---|---|---|---|
| Extra API spending | None required | None initially; limits apply | None initially; paid AI is separate | No API fee; needs suitable user hardware | Usually requires APIs or durable hosting |
| Proposal/asset organisation | Strong with Drive links | Limited attachment capacity on free plan | Small file limit on free plan | Strong locally; weak collaboration/sync unless designed | Strong after build, but not yet |
| Team-friendly current dashboard | Strong with Looker Studio | Good interface view | Basic/limited charts on free plan | Weak by default | Strong after build |
| Existing user environment | Google Workspace enabled; Drive delivery already used | New account/setup | New account/setup | User computer setup required | New build and account decisions |
| Audit/version discipline | Sheet IDs + Drive/GitHub + activity log | Good record controls, but free limits | Better for wiki than strict records | Strong personal history; not group source of truth | Strong after build |
| Suitability now | **Best** | Optional later | Documentation companion only | Private learning companion only | Upgrade after pilot |

## Operating Architecture

| System role | Chosen no-cost-first tool/process | What happens without an API |
|---|---|---|
| Canonical portfolio and approvals | ZYNTH Master Tracker in Google Sheets | Team updates standardised rows/forms; every proposal run updates the same IDs. |
| Asset library | Existing Google Drive and GitHub | The tracker stores links and version metadata; large files remain in their folders/repository. |
| Current dashboard | Looker Studio connected to tracker tabs | Dashboard refreshes from the master sheet data source; it does not need a custom app. |
| Proposal production | Existing Manus production workflow | Research and proposals are produced in the current process; results are registered in the same Master Tracker. |
| AI collaboration | Manual AI Council packet | Send the same fixed brief to available web UIs, copy structured results into the Council tab, then record human resolution. |
| Engineering/change work | GitHub Issues/Projects | Track tracker/dashboard improvements, code, errors, version reviews and future integrations. |
| Learning system | Gemini Notebook for non-confidential source packs, or Obsidian local vault for private personal notes | User asks questions across a controlled library of proposals/research; no API automation is required. |

## First-Pilot Rules

1. One **Master Tracker** is the source of truth. Do not create a new workbook for a new batch.
2. One stable ID represents each campaign, commercial, research claim, task, asset, AI contribution and approval.
3. The next proposal batch creates **10 campaign records and 10 separately numbered commercial/storyboard records**.
4. Each AI product contributes through a manual structured response template until the team proves an automation is useful and safe.
5. Human approval remains required for client-facing claims, budgets, external contacts, public publishing, rights, vendor commitment and personal-data use.
6. The Looker Studio dashboard receives only tabular tracker data; the Drive asset folder stays the document source.
7. Use NotebookLM only for public, approved or de-identified documents. Use Obsidian local vault for any personal/internal learning notes that must stay on the user's device.

## Upgrade Triggers — Do Not Upgrade Before These Are True

| Trigger | Appropriate next upgrade |
|---|---|
| The team runs 3–5 successful manual proposal cycles but data entry is repetitive and error-prone | Add a controlled deterministic update script or form workflow. |
| More than five active contributors need rich role-based collaboration and many asset relationships | Build a Team Board dashboard backed by a database. |
| Research refresh, media monitoring or task status requires unattended execution | Evaluate provider access and one scoped scheduled workflow; approve any cost before activation. |
| The user needs private/offline document analysis and has suitable hardware | Trial local models on the user’s computer, not in the operating system’s shared master data. |
| The portfolio outgrows the free tracker limits or requires advanced permissions | Re-evaluate a paid/no-code database or a custom workspace based on measured needs. |

## What the User Pays Now

**No new API cost is required by this design.** The user may use existing accounts and manual web interfaces subject to those products’ own plan/usage limits. Any later subscription, hardware, hosting or external AI/API cost must be presented as an optional, separately approved upgrade—not an assumption.
