# ZYNTH Interface Audit Notes

**Assessed deployment:** `https://zynth-ai-marketing-firm.up.railway.app/`  
**Assessment date:** 15 August 2026

## Current Interface Findings

The deployed interface already exposes valuable live operating data and commands. It has a branded dark “ZYNTH Command” aesthetic, a proposal constellation, project pipeline, command deck, department status, autonomous switches, proposal search/filtering, and project creation controls. It correctly reflects a founder-control philosophy through a visible “MD-ONLY” automation area.

The core problem is not lack of features. It is that **attention, confidence, and decision flow are not sufficiently structured** for a founder using a mobile/tablet browser. The constellation is visually striking but carries excessive overlapping proposal labels and consumes the first decision surface. The meaningful business information—approval needs, project risks, recent results, source/verification state, current production work, and next decision—is not clearly prioritised above the visual effect.

## Specific Experience Gaps

| Area | Observed condition | Interface implication |
| --- | --- | --- |
| First screen | Large animated agency graph and constellation occupy most visible space. | Put “Today’s Decisions” and verified operating health ahead of ambient visualisation. Keep the constellation as an optional exploration view. |
| Founder workflow | The page offers commands and switches but not a clear inbox of approval-required items. | Add a dedicated approval queue with decision, owner, risk, deadline, evidence status, and approve/revise/archive actions. |
| Information truth | Proposal count, prospect count, financial figures and status are visible but lack per-item source/verification context. | Add “confirmed / observed / hypothesis / stale / needs review” labels and source timestamps. |
| Daily creative work | Proposal cards are visible but do not form a clearly reviewable daily creative package with strategy, concept, rationale, assets, quality score, and production state. | Add a Daily Creative Studio with three focused concept cards and a review/route flow. |
| Production | Image/3D/video work is not a primary founder workflow. | Add a production board with preview, source-file requirement, QA, approval state, output package, and delivery deadline. |
| Mobile/iPad density | Dense text, crowded graphics and long lists reduce scanability. | Design tablet-first split panels, large touch targets, progressive disclosure, short cards, and an optional command palette. |
| Visual hierarchy | Gold/black identity is strong, but the interface uses decorative density rather than restrained contrast to guide decisions. | Preserve the ZYNTH editorial dark style with a calmer command-centre layout, an electric-cyan information accent, restrained gold for selected/approved states, and red only for risks. |

## Recommended Product Structure

1. **Today** — founder decisions, verified health, daily agenda, alerts and one command bar.
2. **Approvals** — real lead/project gates, creative/proposal/production approvals and a decision history.
3. **Opportunities** — filtered project/pipeline/proposal intelligence with evidence and recommendation.
4. **Creative Studio** — daily three-concept packages, brief-to-asset provenance, quality score, 2D/3D/video outputs and production routing.
5. **Delivery** — active project health, timeline, dependencies, risk, scope/margin and deliverable status.
6. **Intelligence** — market/festival/industry calendar, research evidence, outcomes and learning loops.
7. **System** — switches, agents, connections, data freshness and safeguards.

The implementation must preserve existing APIs and live controls, show only information with a visible source/status, and never make external client, vendor, publishing, media-spend, or production decisions automatic.
