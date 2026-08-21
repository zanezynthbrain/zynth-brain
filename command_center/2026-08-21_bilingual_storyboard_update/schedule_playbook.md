# ZYNTH Two-Hour Bilingual Production Playbook

At every run, execute one Myanmar-first agency production batch. Choose exactly one industry that was not used in the immediately preceding run. Choose it from the allowed command-center industry codes: `fnb`, `retail`, `financial`, `telecom-tech`, `hospitality`, `beauty`, `automotive-ev`, `education`, `healthcare`, `real-estate`, `manufacturing`, `entertainment`, `logistics`, `agrifood`, `energy`, `ngo`, `corporate`, `luxury`, `insurance`, or `sports`.

Research first using date-current, public Myanmar, official, local-sector, venue, media, brand, retail, and publisher sources. Do not use unverified claims, private data, invented contacts, bypassed access controls, or fabricated testimonials. Update the historical registry before deciding the industry, event/campaign types, mechanics, creative territories, and budget structures so they do not repeat the immediately prior run.

Produce **10 materially distinct client-pitch-ready concepts for that one industry**, each using a different campaign/event/programme type, commercial tension, conversion mechanism, creative territory, seasonal or special-day logic, and budget structure. Use the September–December 2026 Myanmar calendar only when relevant. Across the ten concepts, consider appropriate forms such as product launch, press preview, exhibition, trade show, roadshow, pop-up, retail activation, sponsorship, executive forum, workshop, masterclass, festival, cultural activation, dealer event, community programme, experiential sampling, influencer-led work, social challenge, paid digital funnel, content series, CRM/reactivation, ABM, omnichannel or commercial-video production. Only propose sponsorship inventory, special days, partner rights, public holidays, permits or venues when the evidence is dated and clear; otherwise label it `proposed/TBC`.

For **each concept**, create two standalone Word documents: one full English version and one English–Myanmar hybrid version. Use natural Unicode Myanmar transcreation for client-facing prose, headings, audience insight, audience journey, messages, CTA examples and approval asks. Retain English only where it is a legal, technical, brand, product, KPI or conventional business term. Each proposal needs cover page, page numbers, distinctive title, Myanmar title, source log, insight, audience behaviour change, experience/campaign plan, seasonal rationale, content system, talent logic, production requirements, Lean/Recommended/Flagship MMK budget packages, separately identified pass-throughs/agency fee/taxes/contingency, sourced assumptions, ROI scenarios, break-even logic, KPI scorecard, risk/compliance, workflow and approval ask. These are planning documents, not supplier quotations, financial guarantees, legal approvals or permit confirmations.

For physical work, create a labelled sketch-design package and a client-viewable 3D-design package showing a hero perspective, front/stage elevation, plan/top view and detail view where feasible. State exact design format, source status, approximate dimensions, materials, surfaces, lighting, furniture, wayfinding, product/talent zones, audience sightlines, production limitations, lead time, complexity, approvals and supplier-engineering requirements. For digital-only concepts, create a campaign UI/experience storyboard instead. Add commercial-video treatment, tagline, storyline, storyboard, production-house/talent/client workflow, pre-production through delivery gate plan and usage-rights approvals when it fits the concept. Include a public, ASMR-ready brand/outreach list only when sensory content is a legitimate strategic fit; never invent a brand contact or commission.

For every applicable concept, add a professional commercial-storyboard treatment rather than a decorative moodboard. The Myanmar-facing version must use natural Myanmar language for the title treatment, audience insight, message, dialogue/VO, on-screen copy, CTA and production notes; the international version must use English. Preserve brand, product, legal, KPI and technical terms in English where appropriate. Each treatment must specify mood, vibe, emotional arc, story premise, audience tension, message-recall logic, tagline, script or VO, dialogue, shot-by-shot storyboard, shot duration, scene location, time of day, framing, camera angle, lens choice, depth of field, camera movement, blocking, actor/talent direction, production design, props, wardrobe, lighting, color palette, color-grading direction, sound design, music, ambience, dialogue recording, edit rhythm, transitions, VFX or practical effects, subtitles, accessibility, cutdowns, aspect ratios, delivery masters and usage rights. Use professional gates: brief and strategy, treatment, script, storyboard, casting/talent, location and permit checks, production design, call sheet, shoot, data backup, offline edit, fine cut, color and sound, client/legal/compliance review, language adaptation, master export, delivery, archive and learnings. Identify owner, client, production house, talent, supplier, approval decision, dependencies, budget, schedule, risks, version number and unresolved TBCs.

Synchronize the 20 Word documents, visual/design files, source files, monitoring report, workbook and source manifest to Google Drive under `ZYNTH Daily Client Proposals` and to the selected GitHub repository under a dated directory. Record only verified Drive folder URLs, GitHub URLs, commit hashes, status and errors. If either destination fails, attempt a reasonable retry, preserve the failure detail, and do not claim synchronization.

## Required Command Center Callback

At the end of every batch—whether complete or failed—POST an auditable JSON status to the published Command Center. The only approved mechanism is the injected scheduled-task environment variables. Do not use another token or URL.

```sh
curl -sS -X POST "$SCHEDULED_TASK_ENDPOINT_BASE/api/scheduled/command-center-sync" \
  -H "Content-Type: application/json" \
  -H "Cookie: app_session_id=$SCHEDULED_TASK_COOKIE" \
  -d '{
    "batchCode":"ZYNTH-YYYYMMDD-INDUSTRY-BILINGUAL",
    "industryCode":"EXACT_ALLOWED_INDUSTRY_CODE",
    "scheduledAt":"ISO_8601_UTC",
    "completedAt":"ISO_8601_UTC",
    "status":"Complete",
    "proposalCount":10,
    "documentCount":20,
    "videoConceptCount":10,
    "driveSyncStatus":"Synced",
    "githubSyncStatus":"Synced",
    "syncRetryStatus":"Not needed",
    "driveSyncedAt":"ISO_8601_UTC",
    "githubSyncedAt":"ISO_8601_UTC",
    "driveFolderUrl":"VERIFIED_DRIVE_FOLDER_URL",
    "githubUrl":"VERIFIED_GITHUB_DIRECTORY_URL",
    "githubCommit":"VERIFIED_COMMIT_HASH"
  }'
```

For a partial or failed run, send the same payload with truthful counts and one of `Pending`, `Failed`, or `Not configured` for each destination, use `Retry scheduled`, `Retrying` or `Exhausted` where applicable, include `lastRetryAt` when a retry is attempted, and include a concise `errorSummary`. A failure callback is mandatory; never silently omit it.

Finally, provide the user a concise report with the selected industry, 10 formats, recommended budget range, scenario-based commercial outcomes, monitoring coverage, exact Drive/GitHub status, and the reminder that the dashboard now contains the auditable lifecycle record.
