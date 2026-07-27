# ZYNTH Departments — how each one runs

Every department is an **AI function that does the work and files it**; only real
owner-decisions reach the MD. The two departments the MD has no experience in get
full standalone systems:
- **Finance** → `FINANCE_operating_system.md`
- **HR** → `HR_operating_system.md`

The rest are below. Each has: what it owns · what it produces (real deliverables, not
task lists) · the skill/tool it works through · what it escalates to the MD. The
"how to do the work" depth lives in the matching skill under `.claude/skills/` — this
file is the "how the department runs" layer.

---

## Marketing (CMO)
- **Owns:** strategy, campaigns, content, paid media, social, SEO, brand.
- **Produces:** complete campaign plans, content calendars, ad plans + results,
  monthly performance reports — the finished documents, ready to run.
- **Works through:** `zynth-master-campaign-planner`, `zynth-brand-strategist`,
  `zynth-content-strategist`, `zynth-copywriter`, `zynth-paid-media-specialist`,
  `zynth-social-media-manager`, `zynth-seo-specialist`, `zynth-analytics-specialist`.
- **Cadence:** weekly client updates by 19:00; monthly reports.
- **Escalates:** media spend commitments; anything client-facing before it's sent.

## Business Development / Sales (BD)
- **Owns:** the pipeline — find prospects, research them deeply, draft outreach, move
  leads through stages.
- **Produces:** enriched prospect records (intel + Apollo contact), ready-to-send
  outreach drafts in the queue, the live BD sheet, pitch prep.
- **Works through:** BD autopilot (`/autopilot`, `/queue`, `/enrich`),
  `zynth-bd-researcher`, `zynth-bd-pitch-prep`, `zynth-market-researcher`,
  `zynth-competitor-analyst`.
- **Cadence:** daily research + enrich + draft; hourly gated sending 9–18.
- **Escalates:** every real send to a prospect (you release from `/queue`).

## Creative
- **Owns:** the big idea, art direction, and craft across formats.
- **Produces:** creative concepts, design direction, video (concept → storyboard →
  edit/grade), copy — the actual creative work, not briefs about it.
- **Works through:** `zynth-creative-director`, `zynth-art-director`,
  `zynth-creative-video-director`, `zynth-video-producer`, `zynth-copywriter`.
- **Escalates:** anything that commits budget (production, talent) or goes to a client.

## Events
- **Owns:** live events end-to-end, one of ZYNTH's two priority revenue lines.
- **Produces:** complete event plans (concept → run-of-show → suppliers → budget →
  funding model → ROI), sponsor packages, run-of-show a stage manager could use.
- **Works through:** `zynth-master-event-planner`, `zynth-event-manager`,
  `zynth-vendor-finder`.
- **Escalates:** venue/vendor commitments; sponsor/ticket pricing sign-off.

## Operations (COO)
- **Owns:** how work gets done — vendors, quality, capacity, process.
- **Produces:** vetted vendor quotes + comparison tables, RFQ emails ready to send,
  the project tracker, capacity forecasts, process SOPs — done, not assigned.
- **Works through:** `zynth-project-manager`, `zynth-vendor-finder`,
  `zynth-campaign-requirements`; knowledge: `05_sops.md`, vendor files.
- **Escalates:** vendor spend; a real capacity crunch that needs a hire (→ HR/Finance).

## Delivery / Portfolio
- **Owns:** the health of live client work and the body of ZYNTH's own assets.
- **Produces:** status of every active project, the proposal library, case studies,
  the "what we've built" record.
- **Works through:** `zynth-account-manager`, `zynth-pitch-packager`; proposal pool.
- **Escalates:** at-risk clients; anything needing an owner conversation.

## Leadership (CEO/MD office)
- **Owns:** the daily rhythm and the through-line across departments.
- **Produces:** the morning brief, EOD summary, weekly review — **short**, decision-
  first, no fake "team velocity" theatre.
- **Escalates:** the few real decisions of the day, each as a clear A/B or yes/no.

---

## The rule every department follows
**Do the work, file it, escalate only owner-decisions.** If a department ever sends
the MD a task instead of a finished thing, that's a bug — fix its agent prompt.
(See `backend/knowledge/00_operating_principles.md`.)
