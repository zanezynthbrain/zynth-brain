# ZYNTH Founder Command Centre

## Product Purpose

The Railway interface is the founder’s **operating surface**, not a decorative status screen. It must help the Managing Director decide what to approve, where to focus, and whether the agency system is producing trustworthy work. Its first responsibility is to reduce uncertainty; its second is to make creativity executable.

## Information Architecture

| Area | Founder question answered | Source of truth | Permitted action |
| --- | --- | --- | --- |
| **Today** | What requires my attention now? | Live system state, directives and project summary | Review, navigate, refresh. |
| **Approvals** | Which real lead or project needs my explicit decision? | Project records with `founder_approval=pending` | Approve or decline with an auditable record. |
| **Creative Studio** | What three ideas are ready for direction, and what production is waiting? | Proposal library and creative queue | Review proposals; select a real project before production routing. |
| **Projects** | Which opportunities and delivery commitments are live, valuable, or at risk? | Project registry | Create founder projects and move an approved project through stages. |
| **Intelligence** | What evidence does the pipeline and proposal factory contain? | Leads, proposal library, outcomes and activity records | Review evidence; queue internal research/proposal work. |
| **System** | Are data sources, agents and automations healthy and controlled? | Connection checks, switch store and command queue | Queue whitelisted internal work; toggle approved internal automations. |

## Data-Truth Rules

Each visible business object must identify its origin and decision state. A founder-created record is labelled **Founder record**. An agent-discovered real project is labelled **Needs confirmation** until the founder approves or declines it. Proposals, research, and generation prompts are labelled **Internal / Review**; they are not treated as client-ready commitments. Connection status is checked at refresh time and must never claim that an unavailable service is healthy.

The interface must not render invented financial, client, performance, or production information. A missing field should be stated as missing rather than inferred. Project-stage transitions remain protected by the existing founder-confirmation guard.

## Interaction Rules

The default landing screen shows four short facts: founder decisions waiting, active projects, pipeline value, and controlled creative queue. The former neural graph and proposal constellation remain suitable as exploratory views, but are not the default decision surface. All controls are designed for touch: large targets, short labels, visible state, and progressive disclosure for technical detail.

| Interaction | Required guardrail |
| --- | --- |
| Approve a real lead/project | Show a confirmation prompt and write a founder decision to the project history. |
| Move project stage | Let the existing backend reject unapproved records from proposal, won, or delivery. |
| Queue a command | State that the action queues internal workflow work only. |
| Toggle automation | Preserve the existing master MD-only control and individual job switches. |
| Review a proposal | Label as internal until the relevant real project has approval and a founder chooses to use it. |
| Creative production | Display prepared queue jobs; do not render, spend, publish, or contact external parties from the interface. |

## Visual Direction

The visual language is **quietly cinematic operational editorial**: deep ink backgrounds, restrained cyan for live/verified information, gold for founder-selected/high-value work, green for healthy/approved states, and warm red only for risk. Dense, animated data visualisation gives way to a spacious tablet-first layout with reading rhythm, short cards, high-contrast touch controls, and a maximum of three primary ideas per section.

## Delivery Scope

The first release replaces the live Railway dashboard renderer without changing its deployment architecture. It consumes the existing JSON state and safe APIs, adds queue-detail data, and retains all existing project, switch, task, command, and proposal endpoints. It deliberately does not change production permissions, model spending rules, client contact, vendor commitments, or publishing rights.
