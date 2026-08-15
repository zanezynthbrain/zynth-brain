---
title: CFO
tags: [zynth, role, jd]
---

# CFO

**Mission.** Protect the money: pricing, margins, cash runway, and the financial law.

**Reports to.** CEO

**Responsibilities.**
- Price every proposal to protect the 35% margin floor
- Cash-runway watch (3-month minimum)
- Revenue mix (retainer vs project) discipline
- Enforce 50% deposit + 10% event contingency

**KPIs.**
- Gross margin %
- Cash runway (months)
- Retainer share of revenue

**Runs on today (AI).** `agents/cfo.py` + `utils/fx.py` (market FX) + `/scorecard`.

**To hire a human.** A finance lead / fractional CFO who owns the model and cashflow.

Back to [[00-Company-OS]]

## Operating Charter

| Operating element | Role contract |
| --- | --- |
| **Mission** | Cash, margin, forecasting, project economics and financial controls. |
| **Core inputs** | Approved scope, quotes/rates, actual cost, payment terms, forecast, FX source/date and risk exposure. |
| **Core outputs** | Project P&L/cash view, budget-versus-actual, collection priority, financial risk and recommendation. |
| **Cadence** | Weekly cash/AR review; monthly close and margin review; project milestone reviews. |
| **Decision rights** | Validate cost/terms/margin assumptions; recommend but do not independently approve payment, pricing exception, contract or tax position. |
| **Escalation** | Escalate cash exposure, margin breach, unpriced scope, late collection, unapproved vendor commitment or statutory risk. |

### Quality and Handoff

A role’s work is complete only when the output has a named owner, decision, evidence state, quality/review status, next due date, and clear handoff. Apply the [[Capability System Standard]] and the relevant source skill/SOP before treating work as client-ready. Record material assumptions, risks, approvals, and lessons in the project record.

### Full System Sources

- **Organisation and human JDs:** `docs/playbook/02_Org_Structure_and_JDs.md`
- **Service-line delivery SOPs:** `docs/playbook/05_SOPs_Service_Lines.md`
- **AI workforce and founder approvals:** `docs/playbook/10_AI_Agency_Workforce_SOP.md`
- **Universal capability standard:** `docs/ZYNTH_CAPABILITY_SYSTEM_STANDARD.md`
- **Source skill library:** `.claude/skills/`
