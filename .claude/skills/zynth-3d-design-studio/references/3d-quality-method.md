# ZYNTH 3D Quality Method — from sketch to vision-proof

The gap between a *sketch* and a *render a client signs off on* is not talent and it is
not the software. It is a fixed list of levers, applied in order. This is that list.

---

## 1. The quality ladder — name the level before you start

Never say "make it good". Say which level, because each level has a cost and a use.

| L | Name | What it is | Looks like | Build time | Use it for |
|---|------|-----------|-----------|-----------|-----------|
| **L1** | **Massing** | Grey boxes, correct dimensions | A floor plan stood up | 30 min | Internal — does the layout work? |
| **L2** | **Blocking** | Massing + brand colours + basic materials | A clean diagram | 1–2 h | Internal review, sightline checks |
| **L3** | **Concept render** | Beveled edges, real furniture, procedural materials, lit | A believable 3D room | 3–6 h | Client concept stage, pitch deck |
| **L4** | **Vision-proof** | L3 + haze/beams, DOF, LED content, dressed tables, reflections | "Is this a photo?" at thumbnail size | 1–2 days | **The pitch render. Sell the job with this.** |
| **L5** | **Photoreal archviz** | L4 + real PBR texture maps, HDRI lighting, asset-library furniture, post-grade | Indistinguishable from a photo | 3–5 days | Final client approval, press, sponsor decks |

**ZYNTH's default deliverable for a pitch is L4.** L5 only when the value of the job
justifies 3–5 days, or when a client rejects L4 as "not real enough".

What the `tools/` scripts in this skill produce today: **L4**, offline, in minutes.
What they cannot reach without asset downloads: **L5** (see §5).

---

## 2. The five levers (in order of visual return)

Apply in this order. Each one is worth more than everything below it.

### Lever 1 — Bevel every hard edge
Nothing in the real world has a perfectly sharp edge. A 2–12 mm bevel catches a
highlight along every edge and instantly removes the "CG plastic" read. This is the
single highest-return change and it costs nothing.

```python
z.bevel(obj, width=0.012, segments=2)     # 12 mm, on furniture and architecture
z.bevel(obj, width=0.03,  segments=2)     # 30 mm, on big structural masses
```

### Lever 2 — Real geometry, instanced
A cube floating where a chair should be is the loudest "sketch" tell in any render.
Build the object *once*, properly, then instance it. 192 chairs then cost the memory
of one chair.

```python
PF_CHAIR = z.prefab_banquet_chair(gold, cloth)   # built once: seat, back, 4 legs, stretcher
z.place(PF_CHAIR, (x, y, 0), rot_z=angle)        # linked duplicate, shares mesh data
```

Rule: **anything that appears more than 3 times must be a prefab.** Anything a guest
would touch (chair, glass, plate, plinth) must be real geometry, not a box.

### Lever 3 — Procedural PBR materials
Flat colour reads as paint. Every real surface has micro-variation in *colour*,
*roughness* and *normal*. Procedural nodes give you all three with no downloads.

| Surface | Recipe | Helper |
|---|---|---|
| Carpet | dense noise → bump, slow noise → colour drift, sheen 0.15, roughness 0.96 | `m_carpet()` |
| Wood | wave (bands) distorted by noise → colour ramp + roughness variation + bump | `m_wood()` |
| Brushed metal | noise stretched on one axis → roughness, metallic 1.0 | `m_metal_brushed()` |
| Polished stone | high-distortion noise → 3-stop veining ramp, roughness 0.07 | `m_marble()` |
| Fabric | noise → bump + **sheen** (sheen is what makes cloth read as cloth) | `m_fabric()` |
| LED screen | image emission × aspect-correct checker pixel grid, **on real UVs** | `m_led_screen()` |

**Roughness variation matters more than colour variation.** A surface with uniform
roughness always looks fake, even with a perfect colour map.

### Lever 4 — Volumetric haze + real beams
This is the #1 cue that separates an *event* render from an *architecture* render.
Every event photo you admire has haze in it. Without a volume, light is invisible;
with it, you get shafts.

```python
z.haze("Haze_room",  (W, L, H), (0,0,H/2), density=0.0026)   # thin, whole room
z.haze("Haze_stage", (24, 15, 8), (0, 15, 4), density=0.023) # dense slab over stage
z.spot("Beam", (x, y, 7.6), target, 14000, colour, angle=7.5, blend=0.14)
```

Calibration that actually works:
- Room haze **0.002–0.003**. Above ~0.004 the whole frame goes milky and flat.
- Stage haze **0.015–0.025** in a *local box*, not the whole room.
- Spots need **10,000 W+** with a **tight cone (6–9°)** to read as a beam.
- **Volumetrics need samples.** Below ~48 samples the denoiser erases faint shafts —
  a beam that "isn't working" at 20 samples often appears at 110. Judge beams only
  at final sample count.

### Lever 5 — Photographic camera and tonemap
- **AgX view transform** (`z.set_render()` sets it). This alone fixes blown-out LED
  walls. Standard/sRGB clips emissive surfaces to flat white — that was the exact
  defect in the v2 renders.
- **Emission strength 1.5–2.5** for LED walls. Not 5. Not 10. Let AgX do the roll-off.
- **Lens 24–35 mm** for interiors; wider distorts, longer can't fit the room.
- **DOF at f/2.8–4.0** focused on the hero object. Depth = "this was photographed".
- **Exposure 0.2–0.4** and then let the room be *dark* — see §3.

---

## 3. Light the room like a lighting designer, not a 3D artist

The most common failure is an evenly-lit room. Real events are **dark rooms with
pools of light**. Contrast is the product.

The rig that works:
1. **Very low ambient** — one big soft ceiling area at *low* power (50–90 W). It exists
   only so shadows aren't black, not to light the room.
2. **Table pools** — one soft downlight per table cluster. This is what a real banquet
   looks like from above.
3. **Stage key + fill** — key strong and warm from front-of-house, fill weak and cool
   from upstage.
4. **Beams** — hard, tight, high-energy spots off the truss. These are the drama.
5. **Accent washes** — booths, entrance arch, cove strips. Low power, brand colour.
6. **Practicals** — candles, LED cove, screens. Emissive materials, strength 1–9.

Ratio rule of thumb: **beam : key : pool : ambient ≈ 150 : 25 : 2 : 1.**

---

## 4. The variety system — one architecture, many art directions

Variety does not mean rebuilding the room. It means swapping a palette dictionary.
`event_scene_build.py` ships five directions; add more by adding a dict entry.

| Key | Direction | Palette | Right for |
|---|---|---|---|
| `aurum` | Gold + navy, warm wood | ZYNTH house, black-tie | Gala dinner, awards, bank/fintech |
| `obsidian` | Monochrome + white light | Minimal, hard-edged | Tech keynote, product launch |
| `emerald` | Emerald + brass, botanical | Lush, natural | Hospitality, property, lifestyle |
| `ember` | Copper + oxblood, moody | Dramatic, low-key | Awards night, whisky/luxury |
| `lumen` | White + ice blue, clean | Clinical, bright | Pharma, medical congress, conference |

```bash
ZYNTH_DIRECTION=emerald ZYNTH_RENDER=iso,stage python3 event_scene_build.py
```

Each direction controls: carpet, wall dark/light, accent metal, accent glow, LED deep/mid,
two beam colours, table cloth, stone base + vein. **Change the palette, the whole room
changes character** — including the generated LED content, which is painted from the
same palette.

**Adding a direction:** copy a dict entry, change the 12 colours, name it after the
feeling not the colour ("midnight-garden", not "dark green").

---

## 5. What we cannot do offline — and exactly how to close it

This environment has **no access to asset libraries** (PolyHaven, BlenderKit, Quixel
are blocked by network policy). That caps us at L4. To reach L5 on a machine with
internet — Zane's laptop, or any studio workstation:

| Missing | Get it from | Wire it in |
|---|---|---|
| **HDRI environment lighting** | polyhaven.com/hdris (free, CC0) | Replace `z.gradient_world()` with an Environment Texture node |
| **PBR texture maps** (carpet, wood, marble, fabric) | polyhaven.com/textures (CC0) | `z.m_textured(name, "/path/to/folder")` — **already written**, auto-detects `_diff`/`_rough`/`_nor` |
| **Real furniture models** | BlenderKit (free tier), Sketchfab CC0 | Import, then use as a prefab with `z.place()` |
| **Real logo / LED content** | Client brand kit | Load PNG → `z.m_led_screen(name, bpy.data.images.load(path))` |
| **Post-grade** | DaVinci Resolve (see `zynth-creative-video-director`) | Render to EXR, grade, add bloom + grain |

`m_textured()` is a working hook, not a plan — point it at a folder and it wires
diffuse, roughness and normal automatically. Nothing else in the pipeline changes.

**Say this to clients honestly:** the concept render is L4, produced in hours; the
photoreal version is L5 and takes days. Never present L4 as final photography, and
never imply a render is a photograph of a real past event.

---

## 6. Self-check before any render goes to a client

Run this list. If any answer is "no", fix it before sending.

- [ ] Is every hard edge beveled?
- [ ] Is anything still a floating cube that should be an object?
- [ ] Does every material have roughness *variation*, not just a colour?
- [ ] Is the room **dark with pools of light**, or evenly lit? (evenly lit = fail)
- [ ] Are beams visible? Did you check at **final sample count**, not a draft?
- [ ] Is the LED wall showing *content*, or a white rectangle? (white = emission too
      high, or no UVs — see the v2→v3 defect log below)
- [ ] Is there depth — foreground, midground, background — or is it one flat plane?
- [ ] Is the camera at **human eye height (1.5–1.7 m)** for the hero shot?
- [ ] Do the scale figures make the space read at the right size?
- [ ] Is the file exported (GLB + FBX + .blend), not just a PNG?

---

## 7. Defect log — real bugs found, so they don't recur

Kept deliberately: each of these produced a visibly wrong render.

| Defect | Symptom | Cause | Fix |
|---|---|---|---|
| **Blown LED wall** | Video wall = flat white rectangle | Emission strength 5–10 + no AgX tonemap | Strength 1.5–2.5, AgX on |
| **Striped screen** | Vertical bands across the LED wall | Texture applied per-panel with no UVs → repeated per object | Build one `curved_screen()` with a real UV map |
| **Inverted curve** | Wall bulged *toward* the audience; black case in front of the screen | Arc centre of curvature on the wrong side | `apex_y` = screen centre, centre of curvature at `apex_y - radius` |
| **Buried wall** | Only the wings of the LED wall visible | Wall apex placed *behind* the back wall | Apex must sit forward of the room shell |
| **Milky frame** | Whole render hazy and flat, no beams | Room haze ≥ 0.004 | Room 0.002–0.003 + dense *local* slab over the stage |
| **Camera in the furniture** | Shooting through chair backs | Camera placed inside the table block | Place cameras outside occupied zones; aim with `z.camera(loc, target)` |
| **Invisible beams** | No shafts despite haze + spots | Judged at 20 samples — denoiser erased them | Judge only at final samples (≥ 96) |
