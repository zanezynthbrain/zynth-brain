# ZYNTH Master Tracker → Google Sheets → Looker Studio Setup

> **Cost:** This setup uses the included workbook and Google’s no-cost dashboard route. It does not require a paid AI API, paid automation or new subscription.

## Part 1 — Make This Workbook the One Living Master Sheet

1. Download `ZYNTH_Zero_Cost_Master_Tracker.xlsx`.
2. In Google Drive, create one permanent folder named **`ZYNTH Marketing Operating System`**.
3. Upload the workbook to that folder and open it with Google Sheets. Choose **File → Save as Google Sheets** if you want the living version to be native to Google Sheets.
4. Keep the file name stable, for example **`ZYNTH_Master_Tracker_LIVE`**. Do not upload a fresh workbook for every campaign batch.
5. Set access carefully: give edit access only to data owners; give comment/view access to reviewers and clients as required.
6. Place every proposal, treatment, storyboard, source pack and report in stable Drive subfolders. Update only the asset link and `Current Version` in the Master Sheet when a document changes.

## Part 2 — Build a No-Cost Looker Studio Dashboard

Google documents that Looker Studio can connect to one Google Sheets worksheet and checks for changed values/new rows when a report query runs. Prepare tabular tabs with a single header row and consistent cell types. [1]

### Data Sources to Add

| Master Sheet tab | Dashboard purpose | Suggested controls |
|---|---|---|
| Campaigns | Campaign portfolio and base-scenario assumptions | Industry, Stage, Status, Owner, Research Confidence |
| Commercials | Commercial studio / storyboard progress | Storyboard Status, Production Status, Rights/Claims, Owner |
| Research & Sources | Source confidence and evidence risk | Confidence, Status, Reviewer |
| AI Council | Manual AI Council actions and human decisions | AI Role, Provider/Tool, Critic Result, Human Decision |
| Ops | Approval queue and delivery blockers | Gate, Priority, Status, Owner |

### Suggested Dashboard Pages

| Page | Core scorecards and charts |
|---|---|
| **Command Center** | Campaign count, commercial count, open decisions, source confidence, at-risk tasks, campaigns by stage/status. |
| **Creative & Commercial Studio** | Commercials by storyboard/production status; campaigns by creative territory; next gate by owner. |
| **Research & Risk** | Sources by confidence; records requiring claim/rights/privacy review; TBC items. |
| **Operations** | Tasks by priority/status; approval decisions; overdue items once due dates are populated. |
| **Learning** | Closed work, reusable mechanisms, proven vs. unproven assumptions and review notes. |

### Build Steps

1. Open [Looker Studio](https://lookerstudio.google.com/), choose **Create → Report**, then choose the **Google Sheets** connector.
2. Select `ZYNTH_Master_Tracker_LIVE` and connect one tab at a time. Use the first row as headers.
3. Create scorecards for status/record counts; create bar charts for campaign stage, commercial storyboard status and operational priority.
4. Add dropdown filters at the page top: `Industry`, `Status`, `Owner`, `Current Stage`, and `Research Confidence`.
5. Set viewer credentials only when viewers should have access to the underlying Google Sheet; otherwise review Google’s owner/viewer credential model before sharing. [1]
6. Record the dashboard URL in the Overview tab or Drive folder description. This link is the team’s dashboard entry point.

## Part 3 — Update Procedure After Every Proposal Run

| Run output | Where to update | How to avoid duplicate files |
|---|---|---|
| New campaign concept | Campaigns tab | Add a new `CMP-...` record only if it is a distinct concept; otherwise update the existing row/version. |
| New commercial idea / storyboard | Commercials tab | Add/update a separate `COM-...` record, optionally link it to a parent campaign. |
| New external fact | Research & Sources tab | Add one source/claim record with URL, date, limitation and reviewer. |
| Manual AI contribution | AI Council tab | Paste concise structured output/link, critic result and human resolution—not raw chat history. |
| Decision or blocker | Ops tab | Add/update the task/approval ID, owner, stage, priority, status and evidence. |
| New proposal/treatment/storyboard file | Drive + record asset link | Put it in the stable record folder; increment Current Version and replace the `Latest Artifact` link. |

## Part 4 — Privacy and Cost Guardrails

Do not enable a paid connector, API, automation, paid AI tier, new subscription or application hosting based on this guide. Use manual structured prompts in AI web interfaces you already have access to. Do not upload client personal data, confidential prices, contracts, unreleased plans or rights-sensitive material to a general AI workspace without an approved data policy.

## Reference

[1] [Google: Connect to Google Sheets in Looker Studio](https://docs.cloud.google.com/data-studio/connect-to-google-sheets).
