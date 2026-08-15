---
title: COO
tags: [zynth, role, jd]
---

# COO

**Mission.** Make delivery reliable: capacity, timelines, quality, and the operating rhythm.

**Reports to.** CEO

**Responsibilities.**
- Resource/capacity planning across departments
- Project timelines and phase gates
- Quality control before anything reaches a client
- Own the weekly cadence

**KPIs.**
- On-time delivery rate
- Revision rounds within scope
- Utilisation vs capacity

**Runs on today (AI).** `agents/operations.py` + `agents/coo.py`; tasks via `/task`.

**To hire a human.** A delivery/ops manager who can run traffic and hold deadlines.

Back to [[00-Company-OS]]

## Operating Charter

| Operating element | Role contract |
| --- | --- |
| **Mission** | Delivery reliability, capacity, quality, margin protection and operating-system integrity. |
| **Core inputs** | Approved scope, timeline, resources, dependencies, project health, capacity, cost/risk and change requests. |
| **Core outputs** | Delivery plan, RACI, traffic/capacity view, risk register, change-control decision and improvement actions. |
| **Cadence** | Daily delivery review; weekly capacity/quality review; monthly systems audit. |
| **Decision rights** | Set operating controls and resource plan within policy; founder/project owner approves material scope, spend, policy and client commitment changes. |
| **Escalation** | Escalate critical path, quality, safety, vendor, margin, client or resourcing failures. |

### Quality and Handoff

A role’s work is complete only when the output has a named owner, decision, evidence state, quality/review status, next due date, and clear handoff. Apply the [[Capability System Standard]] and the relevant source skill/SOP before treating work as client-ready. Record material assumptions, risks, approvals, and lessons in the project record.

### Full System Sources

- **Organisation and human JDs:** `docs/playbook/02_Org_Structure_and_JDs.md`
- **Service-line delivery SOPs:** `docs/playbook/05_SOPs_Service_Lines.md`
- **AI workforce and founder approvals:** `docs/playbook/10_AI_Agency_Workforce_SOP.md`
- **Universal capability standard:** `docs/ZYNTH_CAPABILITY_SYSTEM_STANDARD.md`
- **Source skill library:** `.claude/skills/`
