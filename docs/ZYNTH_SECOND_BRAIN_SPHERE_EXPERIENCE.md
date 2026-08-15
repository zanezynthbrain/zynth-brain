# ZYNTH Second Brain — Sphere Experience Specification

**Purpose:** Replace the flat, static cluster map with a fluid exploratory sphere that lets Zane navigate the real ZYNTH system naturally on desktop and iPad Safari.

> The sphere is an interaction model, not a decorative object. Every visible point must represent a real ZYNTH agent, skill, document, operating record, output, monitor, error or learning asset.

## What the current map does not yet deliver

The existing map groups nodes into fixed two-dimensional regions. It presents real data, but it does not provide the feeling or usefulness of a connected second brain: there is no spatial exploration, continuous zoom, orbiting, contextual depth, or focused navigation through a system relationship.

## The new navigation model

| Founder action | Behaviour |
|---|---|
| **Idle** | The sphere rotates slowly and quietly, revealing the full connected system without demanding attention. Motion pauses for reduced-motion preferences. |
| **Drag with mouse or one finger** | Orbit the sphere in any direction. This changes yaw and pitch instead of moving a flat canvas. |
| **Wheel or pinch** | Zoom toward or away from the system smoothly, with bounded scale so the graph remains readable. |
| **Tap/click a node** | Pause auto-spin, select the real asset, enlarge it, highlight only its direct relationships and open its founder detail drawer. |
| **Double tap/click a hub** | Focus that constellation and ease the camera toward it; related child assets move into the foreground. |
| **Reset control** | Return to the truthful overview, default zoom and gentle rotation. |
| **Lens control** | Filter the sphere to Operations, Capability, Output Lineage, or Health & Learning without replacing the underlying data source. |

## Visual hierarchy

The sphere uses deterministic three-dimensional points generated from the actual current node set. The seven ZYNTH constellation hubs are larger anchor points and stay visually recognisable. Their real child nodes occupy locally coherent territories around each anchor, rather than appearing as arbitrary dots.

| Entity type | Sphere treatment |
|---|---|
| **Constellation hub** | Large orbiting anchor with cluster colour, halo and readable label. |
| **Agent** | Cyan round node. |
| **Skill** | Violet hexagonal node. |
| **Document / research** | Blue soft-square node. |
| **Project / operating record** | Gold round-ring node. |
| **Proposal / creative output** | Gold star/sphere node. |
| **Monitor / switch** | Green ring; amber/coral when the real state requires review or correction. |
| **Mistake / lesson / improvement** | Violet-pink corrective node with a visible loop edge to the improver. |

## Truthful geometry and relationships

The graph projects a real unit sphere into the canvas using a camera yaw, pitch and zoom. Nodes at the rear are naturally smaller and dimmer; they become fully legible as the founder rotates the sphere. Edges are drawn only where their source and target are real connected records in the state model. In overview, the map shows the most meaningful relationship structure; when a node is selected, it prioritises that node’s direct source and result relationships.

The renderer may use depth, opacity, glow and size to improve legibility, but it must not represent node size as commercial value, quality, or execution certainty unless the data model explicitly provides that measure.

## Interaction and accessibility constraints

The build remains dependency-free and canvas-based, avoiding a heavier WebGL/third-party graph runtime for Safari reliability. It supports pointer events, touch pinch, mouse wheel and keyboard-accessible surrounding controls. It respects `prefers-reduced-motion`; in that mode, it renders a static initial view while preserving all pan, zoom and focus interactions. The inventory cards remain a non-graph alternative for users who prefer a list.

## Acceptance criteria

1. The main map is visibly spherical rather than a flat regional layout.
2. Drag, pinch/wheel zoom and node focus work fluidly on iPad Safari and desktop.
3. The map automatically rotates only at an intentionally slow idle speed and never while the founder is touching or focusing it.
4. All data is still drawn from the current Second Brain state; there are no illustrative placeholder nodes.
5. A node selection reveals the same truthful source, relationship, governance and status information as the existing detail drawer.
6. Existing founder approval controls remain untouched and no new external action is introduced.
