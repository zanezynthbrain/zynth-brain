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
`event_scene_build.py` is the AURUM / Novotel Yangon reference (stage, curved LED wall,
runway, truss + lights, 20 round tables, 6 exhibition booths, photo booth, entrance arch,
registration). Clone it, retune the `box()`/`cyl()` calls and materials (`GOLD`, `LEDBLU`,
`SCREEN`…), and re-export for a new brief. To re-skin to a client: change the `GOLD`
base colour and drop a logo plane on `LED_Backdrop` / `Arch_lintel`.

Scope: this is **blocking/massing** quality (clean primitives) for locking layout,
sightlines and flow — the photoreal look comes from the AI render side of the skill.
Outputs (`zynth_3d_out/`, `scratch_out/`) are gitignored — deliver them, don't commit them.
