# ZYNTH Knowledge and Storage Audit

## Confirmed Storage Situation

ZYNTH already has a substantial Google Drive structure. The correct parent is **ZYNTH — Agency OS**, which already contains dedicated folders for Business Development, Creative, Marketing, Finance, Research, SOPs, Proposal Library, Playbook & Reports, Creative Production OS, and an Inbox for review. A separate **ZYNTH-Proposals** library contains an engine folder and sector folders.

This means the correct response is **not** to create a parallel generic Drive folder. New deliverables should be placed under the existing Agency OS and proposal libraries using clear version, status, market, client/sector, and approval labels.

| Asset class | Existing Drive home | Recommended use |
| --- | --- | --- |
| Proposal system, master templates, proposal exemplars | `12 — Proposal Library` and `ZYNTH-Proposals/00 Engine` | Reusable full-proposal standards and approved sector examples |
| Service packages, pricing, growth offers | `01 — Business Development` | Commercial offer architecture and sales enablement |
| Market/competitor research | `10 — Research` | Myanmar/Singapore research, source log, insight notes |
| Full operating playbooks and founder guide | `13 — Playbook & Reports` | Operating-system documents and roadmaps |
| 3D, image, video, and experience materials | `14 — Creative Production OS` | Production briefs, source-file checklists, approved assets |
| Unclassified/new agent output | `99 — Inbox (Needs Review)` | Short-term triage only; no final work should remain here |

## Obsidian Status

ZYNTH’s Obsidian design remains present in the repository. The human-facing Vault is versioned at `vault/ZYNTH-OS/`; the mirror writes selected system documents and live narrative notes into that location. It is therefore connected to GitHub as a repository-backed knowledge base.

The live Railway dashboard currently reports the Vault as missing. This is a runtime-path/configuration issue, not proof that the knowledge base was removed: the deployed process appears to evaluate a relative Vault path from the backend runtime directory while the actual Vault is at the repository root. The mirror maps currently include capability standards, architecture, validation, blueprints, master guides, and live notes; it should be expanded to include the full proposal standard, services/packages, market research, founder brief, and approved proposal index.

## Important Storage Gap

The Railway service’s unattended Drive writer is **not yet active**. It needs a Google service account credential and the chosen target folder ID stored as Railway environment variables. The interactive connected Drive is available in this session and can be organised directly, but the 24/7 bot will continue saving to GitHub only until that configuration is completed.

## Recommended Folder Pattern

Every final deliverable should use a consistent identity:

`YYYY-MM-DD — [Market] — [Client or Sector] — [Asset Type] — [Title] — v01 — [DRAFT/REVIEW/APPROVED]`

Every document should identify its source of truth, owner, market, status, last review date, linked project, approval state, and next decision. This enables Drive, Obsidian, GitHub, and the founder dashboard to point to the same work without confusing draft ideas with client-ready commitments.
