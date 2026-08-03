# ZYNTH 3D Studio — Blender tools (headless)

Build **real, editable 3D event scenes** with no Blender GUI and no GPU — Blender runs
as a Python module.

## Setup (once per session)
```bash
pip install bpy        # Blender as a Python module (bpy 5.x on Python 3.11)
```

## Build a scene
```bash
python3 event_scene_build.py          # exports GLB + FBX + .blend to ./zynth_3d_out/
# or choose a folder:
ZYNTH_3D_OUT=/path/to/out python3 event_scene_build.py
```
Exports:
- `*.glb`  — open on phone / any glTF viewer / SketchUp / Unreal / Spline
- `*.fbx`  — 3ds Max / Maya / Cinema 4D / Unreal
- `*.blend`— full editable Blender file

## Render a still preview (no GPU — Cycles CPU)
```bash
python3 render_preview.py             # writes zynth_3d_out/AURUM_preview.png
ZYNTH_3D_BLEND=/path/scene.blend ZYNTH_3D_PREVIEW=/path/shot.png python3 render_preview.py
```
> EEVEE needs a GPU/EGL context (unavailable headless) — use **Cycles `CPU`** for stills.

## Reuse for any event
`event_scene_build.py` is the AURUM / Novotel Yangon reference build (~682 objects):
navy carpet + warm wood walls + gold LED cornice, gloss stage with a **curved** LED video
wall and gold-framed side panels, truss + alternating blue/gold movers, hedge line, white
runway, 24 round tables with chairs and gold candle centerpieces, 10 illuminated booths,
gold WELCOME arch with real 3D text, photo booth + reception + cocktail poseurs (left),
lounge + catering bar (right), figures for scale, full lighting rig.

Two cameras ship inside the file — **CAM_ISO** (isometric layout) and **CAM_STAGE**
(stage hero). Clone the script, retune the `box()`/`cyl()` calls and materials, re-export.
To re-skin to a client: change the `GOLD` / `NAVY` / `LEDBLU` base colours and drop a logo
plane on `LEDwall_*` / `Arch_top`.

Scope: this is **blocking/massing** quality (clean primitives) for locking layout,
sightlines and flow — the photoreal look comes from the AI render side of the skill.
Outputs (`zynth_3d_out/`, `scratch_out/`) are gitignored — deliver them, don't commit them.


---

## zynth3d.py — the core library

`event_scene_build.py` is one *scene*; `zynth3d.py` is the *toolkit* every scene uses.

| Group | Functions |
|---|---|
| Scene | `new_scene()`, `set_render()` (Cycles CPU + AgX), `out_dir()`, `export()`, `render_shot()`, `stats()` |
| Materials | `m_carpet` `m_wood` `m_metal_brushed` `m_marble` `m_fabric` `m_emissive` `m_glass` `m_led_screen` `m_plain` `m_textured` |
| Screen content | `make_led_content()` — paints a brand LED loop with numpy (no network, no PIL) |
| Geometry | `box` `cyl` `sph` `torus` `curved_screen` (UV-mapped) `bevel` `smooth` `join` `place` (linked instance) |
| Prefabs | `prefab_banquet_chair` `prefab_round_table` `prefab_table_setting` `prefab_truss` `prefab_moving_light` `prefab_person` `prefab_planter` |
| Light | `gradient_world` `area` `spot` `haze` (Principled Volume) |
| Camera | `camera(loc, target, lens, fstop, focus_target)` |

Two rules that carry most of the quality:
1. **Bevel everything.** `z.bevel(obj, 0.012)` — sharp edges are the loudest sketch tell.
2. **Instance anything repeated.** Build a prefab once, `z.place()` it 200 times.

Full method, calibration numbers and defect log: `../references/3d-quality-method.md`.
Reference intake: `../references/reference-pipeline.md`.

## Design directions (variety without rebuilding)

`aurum` (gold/navy gala) · `obsidian` (mono tech keynote) · `emerald` (botanical
hospitality) · `ember` (moody awards) · `lumen` (clean pharma/congress)

```bash
ZYNTH_DIRECTION=ember ZYNTH_RENDER=iso,stage ZYNTH_SAMPLES=110 python3 event_scene_build.py
```
