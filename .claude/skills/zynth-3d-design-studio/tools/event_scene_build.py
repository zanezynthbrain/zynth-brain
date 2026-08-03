"""ZYNTH 3D Studio — headless Blender event-scene builder.

Runs Blender as a Python module (`pip install bpy`) with NO GUI/GPU needed, builds a
corporate-event ballroom scene from primitives (stage, curved LED wall + side panels,
thrust runway, truss + lights, lectern, round guest tables + centerpieces, exhibition
booths, photo booth, entrance arch + registration), and exports GLB + FBX + .blend.

This is the AURUM / Novotel Yangon reference build — clone + retune the boxes for any
event. Real editable geometry (the AI renders are the photoreal mood side).

Run:  python3 event_scene_build.py     (edit OUT below or set ZYNTH_3D_OUT env var)
Preview:  python3 render_preview.py       (Cycles CPU still render, no GPU required)
"""
import bpy, math, addon_utils, os

for a in ("io_scene_gltf2", "io_scene_fbx"):
    try: addon_utils.enable(a)
    except Exception: pass

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

def mk(name, color, metallic=0.0, rough=0.6, emis=None, emis_str=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    def setin(keys, val):
        for k in keys:
            if k in b.inputs:
                b.inputs[k].default_value = val; return
    setin(["Base Color"], (*color, 1)); setin(["Metallic"], metallic); setin(["Roughness"], rough)
    if emis:
        setin(["Emission Color", "Emission"], (*emis, 1)); setin(["Emission Strength"], emis_str)
    return m

CARPET = mk("Carpet", (0.02,0.02,0.045), rough=0.95)
DARK   = mk("DarkWall",(0.02,0.02,0.03), rough=0.8)
GOLD   = mk("Gold", (0.83,0.66,0.22), metallic=1.0, rough=0.3)
BLUE   = mk("Blue", (0.04,0.08,0.22), rough=0.5)
WHITE  = mk("White",(0.90,0.90,0.93), rough=0.7)
RED    = mk("RedCarpet",(0.42,0.03,0.05), rough=0.85)
LEDBLU = mk("LED_Blue",(0.1,0.15,0.4), emis=(0.16,0.36,0.95), emis_str=3.0)
LEDGLD = mk("LED_Gold",(0.4,0.3,0.1), emis=(0.95,0.72,0.25), emis_str=2.2)
SCREEN = mk("Screen",(0.05,0.05,0.08), emis=(0.20,0.30,0.75), emis_str=2.5)

def box(name, dims, loc, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = dims
    o.data.materials.append(mat); return o

def cyl(name, r, d, loc, mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=28)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(mat); return o

# ---- Room ----
box("Floor",        (30,24,0.05), (0,0,0.0), CARPET)
box("BackWall",     (30,0.3,8),   (0,11.9,4), DARK)
box("SideWall_L",   (0.3,24,8),   (-14.9,0,4), DARK)
box("SideWall_R",   (0.3,24,8),   (14.9,0,4), DARK)

# ---- Main stage ----
box("Stage",        (15,5,0.8),   (0,9,0.4), GOLD)
box("Stage_top",    (15,5,0.06),  (0,9,0.83), DARK)
box("LED_Backdrop", (12,0.3,5),   (0,11.4,3.4), SCREEN)   # main video wall
box("LED_Side_L",   (2.2,0.3,4.2),(-7,11.0,3.0), LEDBLU)
box("LED_Side_R",   (2.2,0.3,4.2),( 7,11.0,3.0), LEDBLU)
box("Runway",       (2.6,7,0.4),  (0,4.5,0.2), GOLD)
box("Runway_top",   (2.6,7,0.05), (0,4.5,0.42), DARK)
box("Lectern",      (0.9,0.7,1.2),(-4.5,7.6,1.4), GOLD)
# panel speaker chairs
for i,x in enumerate((2.5,4.0,5.5)):
    box(f"Chair_{i}", (0.7,0.7,0.9),(x,8.8,1.25), DARK)

# ---- Truss + lights over stage ----
for j,yy in enumerate((7.6,10.6)):
    box(f"Truss_beam_{j}", (14,0.3,0.3), (0,yy,6.2), DARK)
for k,(xx,yy) in enumerate([(-6.8,7.6),(6.8,7.6),(-6.8,10.6),(6.8,10.6)]):
    box(f"Truss_leg_{k}", (0.3,0.3,6.2),(xx,yy,3.1), DARK)
import random
random.seed(3)
for m_i in range(8):
    xx = -6 + m_i*1.7
    box(f"Light_{m_i}", (0.35,0.35,0.45),(xx,7.6,5.85), (LEDGLD if m_i%2 else LEDBLU))

# ---- Audience round tables + centerpieces ----
t = 0
for gx in range(-2,3):          # 5 columns
    for gy in range(-4,0):      # 4 rows
        x = gx*4.2; y = gy*3.0 + 3.0
        cyl(f"Table_{t}", 0.9, 0.75, (x,y,0.375), WHITE)
        cyl(f"Center_{t}", 0.16, 0.55, (x,y,1.05), GOLD)
        t += 1

# ---- Exhibition booths along side walls ----
def booth(tag, x, y, face):
    box(f"Booth_base_{tag}", (3,2,0.2),(x,y,0.1), DARK)
    box(f"Booth_back_{tag}", (3,0.2,2.6),(x, y+(1.0*face), 1.3), BLUE)
    box(f"Booth_head_{tag}", (3,0.4,0.4),(x, y+(1.0*face), 2.7), LEDGLD)
    box(f"Booth_screen_{tag}",(1.4,0.12,1.0),(x, y+(0.85*face),1.5), SCREEN)
    box(f"Booth_plinth_{tag}",(0.6,0.6,1.0),(x-1.0, y-(0.4*face),0.5), GOLD)
for i,yy in enumerate((-6,0,6)):
    booth(f"L{i}", -12.5, yy, +1)   # left wall booths face +y? face inward => use face for back offset
    booth(f"R{i}",  12.5, yy, -1)

# ---- Photo booth ----
box("Photo_backdrop", (4,0.3,2.6),(-9,-9,1.3), BLUE)
box("Photo_logo",     (1.3,0.35,1.3),(-9,-8.83,1.5), LEDGLD)
box("Photo_bench",    (2.2,0.6,0.45),(-9,-7.6,0.22), GOLD)
box("Photo_ring_L",   (0.15,0.15,2.2),(-11,-8.8,1.1), WHITE)
box("Photo_ring_R",   (0.15,0.15,2.2),(-7,-8.8,1.1), WHITE)

# ---- Entrance arch + registration + carpet ----
box("Arch_post_L", (0.7,0.7,3.6),(-2.8,-11.4,1.8), GOLD)
box("Arch_post_R", (0.7,0.7,3.6),( 2.8,-11.4,1.8), GOLD)
box("Arch_lintel", (6.9,0.8,0.8),(0,-11.4,3.7), GOLD)
box("Carpet_run",  (3,6,0.03),   (0,-8.5,0.03), RED)
box("Reg_desk_L",  (3,0.9,1.0),  (-6,-9.5,0.5), WHITE)
box("Reg_desk_R",  (3,0.9,1.0),  ( 6,-9.5,0.5), WHITE)
box("Reg_screen_L",(2.2,0.1,0.9),(-6,-9.1,1.6), SCREEN)
box("Reg_screen_R",(2.2,0.1,0.9),( 6,-9.1,1.6), SCREEN)

# ---- Camera + sun (so the .blend opens ready to view) ----
bpy.ops.object.light_add(type='SUN', location=(6,-14,20)); bpy.context.active_object.data.energy=3.0
bpy.ops.object.camera_add(location=(0,-16,7), rotation=(math.radians(74),0,0))
scn.camera = bpy.context.active_object

# ---- Export ----
out = os.environ.get("ZYNTH_3D_OUT", os.path.join(os.getcwd(), "zynth_3d_out"))
os.makedirs(out, exist_ok=True)
n_obj = len([o for o in bpy.data.objects if o.type=='MESH'])
glb = f"{out}/AURUM_Novotel_Event_Stage.glb"
blend = f"{out}/AURUM_Novotel_Event_Stage.blend"
try:
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB'); print("GLB exported")
except Exception as e: print("GLB export failed:", e)
try:
    bpy.ops.export_scene.fbx(filepath=f"{out}/AURUM_Novotel_Event_Stage.fbx"); print("FBX exported")
except Exception as e: print("FBX export failed:", e)
try:
    bpy.ops.wm.save_as_mainfile(filepath=blend); print("BLEND saved")
except Exception as e: print("BLEND save failed:", e)
print("MESH_OBJECTS", n_obj)
