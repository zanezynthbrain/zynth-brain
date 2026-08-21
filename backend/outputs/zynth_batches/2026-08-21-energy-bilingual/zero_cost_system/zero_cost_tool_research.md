# ZYNTH Zero-Cost-First Tool Research

**Research date:** 2026-08-21 UTC

## Decision Standard

A tool is recommended only if it reduces file duplication, is usable without a paid API for the initial pilot, supports a human approval workflow, and has clear limitations. “Free” means no additional software/API spend for the intended pilot. Existing account, device, connectivity and user-subscription conditions may still apply.

| Tool | Verified practical capability | Initial cost path | ZYNTH fit | Recommendation |
|---|---|---|---|---|
| **Google Sheets + Drive + Forms** | Forms can write responses to Sheets; Sheets can be collaboratively edited; Drive files can be linked as artifacts. [1] | No API required. Use existing Google account/workspace access. | Strong source-of-truth for a small team, structured records, asset links, approvals and manual updates. | **Primary master tracker.** |
| **Google Looker Studio** | Google describes Data Studio/Looker Studio as a no-cost dashboard tool. It connects to a Sheet worksheet and checks for changed values/new rows when queries run. [2] [3] | No API required for a Google Sheets data source. | Converts the single Master Sheet into a current shared dashboard without building an app. | **Primary dashboard.** |
| **GitHub Projects** | Provides table, board, roadmap, custom fields, built-in automation, charts, status updates and two-way syncing with issues/PRs. [4] | No paid API needed for manual/project-board use; existing GitHub repository is already available. | Excellent for technical build tasks, workflow changes, validation and version review; less friendly as the main marketing portfolio home. | **Secondary technical board.** |
| **Gemini Notebook / NotebookLM** | Supports Drive files, Docs, Sheets, Word, Markdown, PDFs, URLs and more; free users can include up to 50 sources per notebook; imported Drive sources can synchronize when the notebook opens. It cites source-based responses. [5] [6] | No API required. Product access/usage limits may change. | Best for the user's learning: ask questions across proposal archives and source packs, produce study material and compare evidence. | **Recommended learning room, with privacy rule.** |
| **Obsidian** | No sign-up is required; data is stored locally; optional Sync/Publish services cost separately. [7] | Core local app can be used without a paid API or subscription. | Strong personal proposal/learning library, fully local Markdown files and long-term knowledge organisation. Collaboration/sync needs a separate chosen process. | **Recommended optional personal knowledge vault.** |
| **Airtable Free** | Free plan lists 1,000 records/base, up to 5 editors, 1 GB attachments/base and 100 automation runs. [8] | No cost for the stated limits; avoid its AI/paid features. | Good interface/board option if the team prefers database views over Sheets; limits make it unsuitable as the long-term asset home. | **Optional lightweight alternative.** |
| **Notion Free** | Includes databases and basic forms; individual free workspace has unlimited pages/blocks, but multi-member Free workspaces have a limited block allowance; file uploads are up to 5 MB. [9] | No paid API required; avoid paid AI/credits. | Good proposal wiki and meeting documentation, but not suitable as the canonical binary-asset library or unrestricted multi-user database. | **Optional documentation layer only.** |
| **Ollama local models** | Runs on macOS, Windows and Linux; local endpoint does not require authentication, while cloud/API usage is separate. [10] [11] | No API charge for local model inference; uses the user's computer, storage, electricity and sufficient hardware. | Private/offline experimentation and local summarisation; quality and speed depend on device and it is not the first pilot path. | **Optional later fallback, not initial core.** |

## Recommended Zero-Cost-First Stack

| Need | Chosen tool/process | Why this is the recommended first choice |
|---|---|---|
| Source of truth | **Google Sheets Master Tracker** | Familiar, portable, collaborative, supports a controlled data dictionary and can link all existing Drive/GitHub artifacts. |
| Asset home | **Existing Google Drive + GitHub** | Keep heavy assets/proposals outside the sheet; link versions by stable ID. |
| Current dashboard | **Google Looker Studio** reading the tracker | No custom app or API is required; sheet changes appear through the connector refresh process. |
| Intake and approvals | **Google Forms / controlled Sheet dropdowns** | Prevents invalid status values and creates a recorded decision pathway. |
| Proposal production | **Current Manus workflow** plus versioned output folders | Continues the current bilingual proposal production without external API dependence. |
| AI Council | **Manual structured hand-off** | Paste a fixed brief into whichever AI web interface the user already has access to; paste the returned artifact into the AI Council sheet. No API key, unattended automation or extra charge is required. |
| Learning library | **Gemini Notebook (non-confidential only) or Obsidian (local)** | Lets the user study proposal/source packs rather than searching folders. |
| Technical work | **GitHub Projects** | Tracks the tracker/dashboard build and future automation as issues with reviewable changes. |

## Explicit Non-Recommendations for the Initial Pilot

Do not start with a paid API orchestrator, paid multi-agent platform, always-on server, Zapier/Make-style paid automation, self-hosted workflow engine, or local-model setup. These add cost, credentials, maintenance or hardware risk before the team has validated its process. Use manual structured AI contributions first; only automate a repeated, measurable step after 3–5 successful cycles.

## Privacy Rule for the Learning Tool

Use Gemini Notebook only for public, approved or de-identified material unless the user has a qualifying Workspace account and has verified the account-specific privacy controls. Google states that, for general users, feedback can include associated content for review and product improvement; Workspace/education users have different protections. [6] Never upload client personal data, confidential rates, unreleased commercial plans or rights-sensitive material without the client-approved data policy.

## References

[1] [Google Forms: Create and analyze forms](https://support.google.com/docs/answer/6281888).  
[2] [Google Cloud Data Studio documentation](https://docs.cloud.google.com/data-studio).  
[3] [Connect to Google Sheets in Data Studio](https://docs.cloud.google.com/data-studio/connect-to-google-sheets).  
[4] [GitHub Projects: About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects).  
[5] [Google Notebook: Add or discover sources](https://support.google.com/gemininotebook/answer/16215270?hl=en).  
[6] [Google Notebook: Privacy and terms](https://support.google.com/gemininotebook/answer/17004255?hl=en).  
[7] [Obsidian pricing and privacy information](https://obsidian.md/pricing).  
[8] [Airtable pricing](https://www.airtable.com/pricing).  
[9] [Notion pricing](https://www.notion.com/pricing).  
[10] [Ollama quickstart](https://docs.ollama.com/quickstart).  
[11] [Ollama authentication](https://docs.ollama.com/api/authentication).
