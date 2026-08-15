# ZYNTH Second Brain — Information Architecture and Interaction Model

**Audience:** Zane, Managing Director  
**System:** ZYNTH Founder Command on Railway  
**Purpose:** A creative, founder-facing map of the real ZYNTH operating system: the agents, skills, documents, data, work outputs, health signals, approval gates, errors, lessons and improvement loops that are already present in the repository and live service.

> **Design premise.** The Second Brain must feel like a living creative intelligence system, but it must never invent activity. Every visible node, value, relationship, alert and action is derived from a named ZYNTH source. A visual effect is valid only when it communicates a real state, dependency, flow, risk, or decision.

## 1. The founder’s question set

The Second Brain is designed to answer five questions without asking the founder to search folders or read code.

| Founder question | Second Brain answer |
|---|---|
| **What is ZYNTH made of?** | The live map displays real capability hubs: agents, skills, knowledge, data, outputs, operations, monitoring and learning. |
| **What created this output?** | The detail drawer exposes the generating workflow, relevant capability, governing documents, project state and approval boundary. |
| **What is active, blocked or awaiting me?** | Pulses, health panels, approvals, operating queues and error/lesson nodes reflect the current system state. |
| **Where is the source of truth?** | Each node gives the repository path or live data source from which it was created. |
| **What improves the system over time?** | The map makes the feedback loop visible: activity/error → mistake log → lesson/improver → skill/document/process → future output. |

## 2. Information model: seven connected constellations

The main map uses seven distinguishable constellations. They are intentionally fewer than the number of files so the founder sees a system rather than a visual dump.

| Constellation | Real sources | Node examples | Meaning of an edge |
|---|---|---|---|
| **Agency Core** | `backend/agents/`, agent runtime specifications | CEO, CMO, COO, Master Proposal, Market Researcher, Video Team, Improver | An agent **uses**, **orchestrates**, **reviews**, or **improves** another capability. |
| **Capabilities** | `.claude/skills/*/SKILL.md` | 3D Design Studio, Commercial Video Studio, Master Proposal Writer, Art Director, ICP, Sponsorship Value | A capability is **available to** an agent or **governs** an output type. |
| **Knowledge & Second Brain** | `docs/`, `research/`, `vault/ZYNTH-OS/`, proposal exemplars | Proposal Standard, Service Packages, Founder Operating Model, Market Research, Design/Animation Assessment | A document **informs**, **sets a standard for**, **records**, or **is mirrored into** the Second Brain. |
| **Operating Data** | projects, prospects, leads, tasks, venues, suppliers, finance and scorecard utilities | Project portfolio, hot prospects, tasks, finance scorecard, events, vendors | Data **feeds** a workflow, **qualifies** a project, or **measures** an outcome. |
| **Outputs & Production** | proposal library, creative queue, daily workforce, proposal pool and deliverables | Internal concepts, full proposals, storyboard packages, 3D/Blender briefs, queued creative jobs | An output is **created by**, **reviewed through**, **requires**, or **belongs to** a project. |
| **Monitoring & Control** | connections, switches, cost audit, command queue, project approvals | Railway connections, Drive, Obsidian, GitHub, autonomy switches, API budget, founder approval | A control **monitors**, **blocks**, **enables**, or **alerts**. |
| **Learning & Improvement** | mistakes, lessons, outcomes, improver, review board | Error log, lesson library, self-improvement review, outcomes, quality check | A failure or outcome **creates a lesson** that **improves** future capability. |

### Relationship language

Edges use a small fixed set of labels. This makes the map legible and avoids decorative lines.

| Edge label | Example |
|---|---|
| **uses** | Master Proposal Agent → Master Proposal Writer skill |
| **informed by** | Master Proposal Agent → Full Client-Grade Proposal Standard |
| **creates** | Daily Workforce → Internal Concept Package |
| **routes to** | Approved Project → Creative Queue |
| **requires approval** | Creative Queue → Founder Approval Gate |
| **monitors** | Connections Health → Google Drive writer |
| **records** | Mistakes Log → Improvement Lesson |
| **improves** | Improver Agent → Capability System Standard |
| **mirrors to** | Knowledge document → Obsidian vault note |
| **measures** | Outcome/Scorecard → Project or Campaign |

## 3. Visual language: original ZYNTH "Signal Garden"

The visual direction adapts the useful principles from the reference—high-information density, a central connected view, status-at-a-glance, dark focus and a detail-on-demand model—without copying its exact look or creating meaningless sci-fi decoration.

| Design layer | Direction |
|---|---|
| **Background** | Deep ink-blue/green with a restrained radial glow. The space is calm enough for daily decision work and lets creative artifacts take visual priority. |
| **Type** | Inter/system sans for primary content; an iPad-safe monospace face only for paths, IDs, dates, health diagnostics and compact metadata. |
| **Colour** | Cyan = capability/active knowledge; gold = output/value/creative work; green = healthy/approved; amber = pending/review; coral = error/blocker; violet = learning/improvement; muted slate = inactive/reference. |
| **Nodes** | Distinct shapes and sizes by entity type: rounded hubs for agents, hex/diamond capability nodes, document tabs for knowledge, spheres for outputs, rings for monitoring, and small corrective diamonds for errors/lessons. |
| **Edges** | Thin, labelled only in focus view. A moving pulse appears only for a real active job, live queue, approval waiting state or detected health alert. |
| **Density** | The overview renders only the seven hubs and a curated sample of real child nodes. Cluster, filter and detail modes reveal the full inventory on demand. |
| **Motion** | Short purposeful transitions; reduced motion respected. No automatic camera movement, parallax, or animated background that makes the founder wait to read a real state. |

## 4. Founder interaction model

### 4.1 Primary modes

The founder begins with **Overview** and can switch between five specific lenses.

| Lens | What it prioritises | Founder use |
|---|---|---|
| **Overview** | The seven constellations, top outputs, current approvals, overall health and active operating pulse. | A two-minute daily orientation. |
| **Operations** | Departments, projects, proposal/workforce activity, queues, tasks, switches and pipeline. | Decide what should run, pause, review or advance. |
| **Capability** | Agents, skills, governing standards, documents and their relationships. | Confirm whether ZYNTH can credibly execute a request and identify gaps. |
| **Output lineage** | Concepts, proposals, project records, creative jobs and approval state. | Trace what generated an output and what remains before a client-ready release. |
| **Health & learning** | Connection diagnostics, costs, errors, lessons, self-improvement and alerts. | Resolve blockers and decide what to improve. |

### 4.2 Node detail drawer

Selecting a node opens a right-side detail drawer on desktop/tablet and a full-height bottom sheet on iPad portrait. The drawer contains the truthful metadata first, then the possible next action.

| Drawer section | Required content |
|---|---|
| **Identity** | Name, entity type, status, source path or data source, and last known update. |
| **Role** | What this agent/skill/document/output does in plain founder language. |
| **Connections** | Parent/source nodes, child/result nodes and the relationship label. |
| **Evidence** | Real counts, state, known assumption, health details, project/approval state or document reference. |
| **Governance** | Whether it is Explore-only, founder-gated, client-ready, blocked or external-release restricted. |
| **Action** | Only existing safe actions: open the document, review output, view project, queue internal workflow, or resolve a defined diagnostic. No unapproved external action. |

### 4.3 Mobile/iPad behaviour

The graph is an enhancement, not a requirement for use. On narrow screens, the map collapses to an ordered list of the seven constellations with status, counts and a horizontally scrollable relationship preview. Tapping a constellation opens its actual child-node list and detail sheet. The overview remains usable with touch, Safari and reduced-motion settings.

## 5. Honest status model

The interface uses six status states, always driven by source data.

| Status | Display | Source examples |
|---|---|---|
| **Healthy / available** | Green ring or dot | Live connection check passes; capability/document exists; an approved project route is valid. |
| **Active internal work** | Cyan/gold pulse | An enabled scheduled workstream, queued internal command, or pending internal creative job. |
| **Founder review required** | Amber outer ring | Pending founder project approval, output review, or production route blocked by approval. |
| **Blocked / error** | Coral error diamond | Connection diagnostic down, failed work recorded in mistakes log, blocked writer configuration. |
| **Reference / dormant** | Slate node | Existing capability or document not currently used by an active workflow. |
| **Learning / improvement** | Violet loop indicator | Mistake, lesson, review or improver action that feeds future work. |

## 6. Technical architecture

The interface remains dependency-free, consistent with the existing command centre. It does not introduce a React build, external graph CDN, or a new service. This preserves the Railway deployment model and iPad/Safari reliability.

| Component | Implementation approach |
|---|---|
| **Graph data** | New `utils.second_brain.build_state()` scans named repository locations and joins live state from the existing `dashboard`, `connections`, `switches`, `projects`, `creative_queue`, `mistakes`, `proposal_library` and task/proposal structures. |
| **Graph view** | A self-contained HTML/CSS/JavaScript canvas/SVG interface, derived from real JSON. Canvas handles the ambient constellation; accessible HTML overlays handle labels, controls, detail cards and actions. |
| **Routing** | A new `/second-brain` GET route in the existing Railway HTTP handler and a read-only `/api/second-brain` state route. Existing action routes remain the sole source for any control mutation. |
| **Data freshness** | Initial state is embedded server-side; client refreshes the read-only graph state periodically and on founder lens changes. No browser state is treated as the source of truth. |
| **Performance** | Overview node count is capped; no real 3D renderer; heavy assets never load inside the map; node movement is modest and paused under `prefers-reduced-motion`. |
| **Security / governance** | No source-code contents, environment values or secrets appear in node metadata. External actions cannot be triggered from graph nodes. |

## 7. First-release scope

The first release should make the existing system visible and usable rather than attempting a full knowledge-graph platform.

| Included in release one | Deliberately deferred |
|---|---|
| Live 7-cluster overview, actual agent and skill inventory, curated standing documents, real project/proposal/queue state, connection health, active switches, mistakes/lessons counts, detail drawer, filters and iPad-safe responsive mode. | Editing arbitrary documents in the graph, external knowledge crawling, automatic diagram creation from unverified sources, 3D WebGL background, full historical time travel, raw code visualisation, or new automation privileges. |
| Direct links to actual source paths/documents and the existing safe command/review routes. | Automatic client contact, publication, spend, vendor booking or any action that bypasses current founder approval gates. |

## 8. Acceptance criteria

The Second Brain is ready for founder use when all statements below are true.

1. Every top-level cluster and child node represents a real repository asset, live data set, output, monitored integration, or documented operating construct.
2. The founder can identify whether a project/output is internal, approved, pending, blocked or released without relying on colour alone.
3. Selecting an output makes its creating workflow, related capability, source/standard and approval state visible.
4. Monitoring and error nodes use the existing connection and mistake records; they do not show simulated alerts.
5. The map remains fast and legible on Safari/iPad and provides a list/card alternative on smaller screens.
6. Existing founder gates for client contact, publication, spend, booking and production remain unchanged and accessible from their current controlled routes.
7. The Second Brain adds understanding, not another duplicate operating system.

---

**Operating principle:** ZYNTH’s Second Brain is not a visualisation of possible work. It is a creative, connected view of the agency’s actual capability, evidence, work in progress, controls and learning.
