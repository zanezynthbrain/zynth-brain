# ZYNTH Reference Pipeline — from Pinterest to a buildable 3D direction

How a picture Zane likes becomes a design direction the 3D builder can actually execute.
The point of this pipeline is that **references stop being "vibes in a chat"** and become
a structured card that drives real parameters.

---

## The honest constraint first

Claude sessions **cannot browse Pinterest or Behance directly.** Pinterest is
login-walled and scrape-blocked; in the Railway/agent environment most external image
hosts are blocked by network policy entirely. Anyone who tells you an agent "pulled
references from Pinterest" is describing something that did not happen.

**What works instead:** Zane (or an intern, in 15 minutes) collects the images and drops
them in. Claude reads images natively — it can extract palette, materials, lighting,
layout and mood from a JPEG with high accuracy. The human does the *taste*; the pipeline
does the *translation*.

This is not a workaround. Curating references is the art-direction job and should stay
with a human anyway.

---

## The pipeline

```
  1  COLLECT      Zane pins / saves 8–15 images per project
        ↓
  2  DROP         into Drive  ZYNTH-Creative/References/<Client>-<Project>/
                  or straight into a Claude session
        ↓
  3  EXTRACT      Claude reads them → writes a Design DNA card (§ below)
        ↓
  4  DIRECTION    card → a DIRECTIONS entry in event_scene_build.py
        ↓
  5  BUILD        ZYNTH_DIRECTION=<key> python3 event_scene_build.py
        ↓
  6  COMPARE      render side-by-side with the references; log the gap
        ↓
  7  REFINE       tune palette / lighting / detail; repeat 5–6 until it matches
```

Steps 3–7 are Claude's. Steps 1–2 are 15 minutes of human work and cannot be skipped.

---

## Step 1 — Collecting references that are actually useful

Most reference boards are useless because they are all the same shot. Collect **by
category**, not by "things I like":

| Category | How many | What to look for |
|---|---|---|
| **Stage / focal structure** | 3–4 | The hero shot. Screen shape, framing, how the stage meets the floor |
| **Room-wide / layout** | 2–3 | Wide or top-down. Table density, circulation, where zones sit |
| **Lighting mood** | 2–3 | Beams, colour temperature, how dark the room is |
| **Material close-ups** | 2–3 | Carpet, drape, metal finish, stone. The *texture*, not the object |
| **Detail moments** | 2–3 | Table setting, booth, entrance arch, photo wall |
| **Anti-references** | 1–2 | "Not this." Sharpens the direction faster than anything else |

Source them anywhere: Pinterest, Behance, event-production company portfolios
(Sparq, TBA, Bruce Rodgers), venue galleries, awards sites (Event Marketer, BizBash),
ArchDaily for materials. Save the actual image files.

**Rights note:** references are for internal direction only. Never put a competitor's
photo in a client deck, never present a reference image as ZYNTH's own work, and never
claim a reference is a past ZYNTH event.

---

## Step 2 — Where they live

```
Google Drive
└── ZYNTH-Creative/
    └── References/
        └── <Client>-<Project>/
            ├── 01-stage/
            ├── 02-layout/
            ├── 03-lighting/
            ├── 04-materials/
            ├── 05-details/
            ├── 00-ANTI/
            └── DESIGN-DNA.md      ← the output of step 3
```

Mirror to the repo under the project folder so the DNA card is versioned with the build
script that consumed it.

---

## Step 3 — The Design DNA card

This is the deliverable of the pipeline. Every field maps to something the builder can
execute. Vague fields ("elegant", "premium") are banned — if it can't become a number
or a named material, it doesn't go on the card.

```markdown
# DESIGN DNA — <Client> <Project>
Refs: 12 images | Extracted: <date> | Direction key: `<key>`

## Palette                      (hex + role — pulled from the reference pixels)
- Ground / carpet     #070B21   deep navy, low reflectance
- Wall field          #2A1810 → #4A2F17   warm wood, two-tone grain
- Accent metal        #D4A537   brushed gold, NOT mirror
- Accent glow         #FFC24D   LED cove + edge lighting
- Screen deep         #05173F   LED background
- Screen mid          #0F42B8   LED mid-tone
- Beam warm           #FFC761
- Beam cool           #5A8CFF

## Materials                    (surface → finish → roughness estimate)
- Floor      cut-pile carpet, matte, rough ~0.95, visible nap
- Stage deck polished stone, rough ~0.07, strong reflection ← key to the look
- Frames     brushed brass, anisotropic streak along the long axis, rough ~0.26
- Drape      heavy velvet, high sheen, deep folds
- Tables     matte linen, slight sheen

## Lighting
- Overall level:    DARK — room reads ~15% lit, pools only
- Key direction:    front-of-house, warm, high contrast
- Beams:            YES — 8–12 tight shafts, visible haze, two colours alternating
- Practicals:       LED cove strips, candle votives, screen spill
- Colour contrast:  warm gold key vs cool blue fill

## Structure & layout
- Screen:      curved, ~20 m wide, ~6 m tall, gentle wrap (radius ≈ 22 m)
- Stage:       1.0 m riser, thrust into audience, steps centre-front
- Seating:     24 rounds of 8, centre aisle / runway
- Perimeter:   illuminated booth portals both walls
- Entrance:    lit arch, runner, registration to one side

## Mood in three words
<e.g. "restrained, molten, ceremonial">

## Anti-references — explicitly NOT this
- Not evenly lit / conference-bright
- Not chrome or mirror-finish metal
- Not cool-white LED

## Build parameters                (copy straight into DIRECTIONS)
carpet=(0.030,0.045,0.130), wall_dark=(0.115,0.070,0.032), ...
```

---

## Step 4 — Card → direction, mechanically

The card's **Palette** block converts straight to a `DIRECTIONS` entry. Blender wants
linear-ish 0–1 floats, so from hex:

```python
def hex_to_rgb(h, gamma=2.2):
    h = h.lstrip("#")
    return tuple(round((int(h[i:i+2], 16) / 255.0) ** gamma, 3) for i in (0, 2, 4))

hex_to_rgb("#D4A537")   # -> (0.646, 0.377, 0.036) ... then taste-adjust
```

Then the **Lighting** block sets the rig (§3 of `3d-quality-method.md`), the
**Structure** block sets the geometry constants (`ARC_APEX`, `ARC_R`, `STAGE_*`,
table grid), and **Materials** picks which `m_*` helper each surface uses.

Nothing here is guesswork — every card field has one destination.

---

## Step 5–7 — Build, compare, refine

Render the same two framings as the strongest references (usually one wide/iso and one
stage hero), put them side by side, and write down the gap in the same vocabulary as
the card:

> "Reference stage is 40% darker than ours; beams are tighter and there are more of
> them; our gold is too yellow — reference brass is browner; reference has floor
> reflection we're missing."

Then fix in **§2 lever order** — geometry before materials before lighting before
camera. Two or three loops is normal. Log what you changed in the defect log so the
next project starts closer.

---

## Turning this into a library over time

Every completed project leaves behind: a DNA card, a `DIRECTIONS` entry, and the final
renders. After ~8 projects ZYNTH has a house library of directions that can be pitched
*instantly* — "here are five directions for your gala, pick one" — with real renders
attached, all generated by ZYNTH, none borrowed. That library is the actual asset being
built here, not any single render.
