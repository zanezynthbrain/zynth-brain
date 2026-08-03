"""ZYNTH 3D Studio — headless Blender event-scene builder (AURUM v2).

Blender as a Python module (`pip install bpy`) — no GUI, no GPU. Builds a full
corporate-event ballroom matched to the AURUM reference art direction:
navy carpet + warm wood walls + gold LED cornice, raised gloss stage with a CURVED
LED video wall and gold-framed side panels, truss + alternating blue/gold movers,
hedge line, white runway, ~24 round tables with chairs and gold candle centerpieces,
10 illuminated exhibition booths (5 per wall), gold WELCOME arch with real 3D text,
photo booth + reception + cocktail poseurs (left), lounge + catering bar (right),
figures for scale, and a full lighting rig. Two cameras are saved in the file:
CAM_ISO (isometric layout) and CAM_STAGE (stage hero).

Exports GLB + FBX + .blend. ~682 objects.

Run:      python3 event_scene_build.py            # -> ./zynth_3d_out/ (or $ZYNTH_3D_OUT)
Preview:  python3 render_preview.py               # Cycles CPU still (EEVEE needs a GPU)
Re-skin:  change the GOLD / LEDBLU / NAVY materials and retune the box()/cyl() calls.
"""
import bpy, math, addon_utils, os, random, mathutils
random.seed(7)

def aim(cam, target):
    d = mathutils.Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z','Y').to_euler()

for a in ("io_scene_gltf2", "io_scene_fbx"):
    try: addon_utils.enable(a)
    except Exception: pass

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

# ---------- materials ----------
def mk(name, color, metallic=0.0, rough=0.6, emis=None, emis_str=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    def setin(keys, val):
        for k in keys:
            if k in b.inputs: b.inputs[k].default_value = val; return
    setin(["Base Color"], (*color, 1)); setin(["Metallic"], metallic); setin(["Roughness"], rough)
    if emis:
        setin(["Emission Color", "Emission"], (*emis, 1)); setin(["Emission Strength"], emis_str)
    return m

NAVY   = mk("NavyCarpet",(0.03,0.045,0.13), rough=0.92)
WOOD   = mk("WarmWood",  (0.16,0.11,0.06),  rough=0.55)
GOLD   = mk("Gold",      (0.83,0.65,0.22),  metallic=1.0, rough=0.28)
GOLDEM = mk("GoldGlow",  (0.5,0.36,0.12),   emis=(0.95,0.72,0.26), emis_str=2.4)
WHITE  = mk("White",     (0.90,0.90,0.92),  rough=0.6)
WHITEE = mk("WhiteGlow", (0.85,0.86,0.9),   emis=(0.9,0.92,1.0), emis_str=2.6)
GLOSS  = mk("StageGloss",(0.02,0.02,0.035), metallic=0.4, rough=0.08)
LEDBLU = mk("LED_Blue",  (0.06,0.12,0.4),   emis=(0.14,0.3,0.85), emis_str=1.5)
LEDCYN = mk("LED_Cyan",  (0.1,0.2,0.35),    emis=(0.3,0.6,1.0), emis_str=2.0)
BLACK  = mk("Black",     (0.02,0.02,0.025), rough=0.7)
GREEN  = mk("Plant",     (0.04,0.18,0.06),  rough=0.7)
CANDLE = mk("Candle",    (1.0,0.7,0.35),    emis=(1.0,0.62,0.25), emis_str=6.0)
LINEN  = mk("Linen",     (0.92,0.9,0.86),   rough=0.65)
SOFA   = mk("Sofa",      (0.52,0.5,0.46),   rough=0.75)
SKIN   = mk("Skin",      (0.6,0.42,0.32),   rough=0.6)
SUIT   = mk("Suit",      (0.06,0.07,0.1),   rough=0.6)
REDG   = mk("RedBottle", (0.5,0.05,0.08),   rough=0.3)
AMBER  = mk("Amber",     (0.6,0.35,0.05),   rough=0.3)

# ---------- primitives ----------
def box(name, dims, loc, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = dims
    o.data.materials.append(mat); return o

def cyl(name, r, d, loc, mat, verts=24, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=verts, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(mat); return o

def sph(name, r, loc, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=12, ring_count=8)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(mat); return o

# ---------- room ----------
box("Floor",   (32,42,0.05), (0,0,0),   NAVY)
box("BackWall",(32,0.3,10),  (0,20.9,5),WOOD)
box("WallL",   (0.3,42,10),  (-15.9,0,5),WOOD)
box("WallR",   (0.3,42,10),  (15.9,0,5), WOOD)
# gold LED cornice strip near top of each wall
box("Cornice_B",(31,0.15,0.25),(0,20.7,8.2),GOLDEM)
box("Cornice_L",(0.15,41,0.25),(-15.7,0,8.2),GOLDEM)
box("Cornice_R",(0.15,41,0.25),( 15.7,0,8.2),GOLDEM)
# wood pilasters down the side walls
for yy in range(-18,20,5):
    box(f"Pil_L_{yy}",(0.35,1.2,7.5),(-15.6,yy,4.5),WOOD)
    box(f"Pil_R_{yy}",(0.35,1.2,7.5),( 15.6,yy,4.5),WOOD)

# ---------- main stage ----------
box("Stage",     (19,7,1.0), (0,17.5,0.5), BLACK)
box("Stage_top", (19,7,0.06),(0,17.5,1.03),GLOSS)      # glossy dark deck
box("Stage_trim",(19.2,7.2,0.12),(0,17.5,0.98),GOLDEM) # gold edge glow
# curved LED video wall (arc of segments), concave toward audience
Cx,Cy,R = 0.0, 33.0, 13.0
segs = 11
for i in range(segs):
    phi = math.radians(-38 + i*(76/(segs-1)))
    x = Cx + R*math.sin(phi); y = Cy - R*math.cos(phi)
    box(f"LEDwall_{i}", (2.55,0.2,5.6), (x,y,3.9), LEDBLU, rot=(0,0,phi))
# gold side panels flanking the wall (with medallion emblem)
for s,sx in ((0,-8.6),(1,8.6)):
    box(f"SidePanel_{s}", (2.6,0.25,5.6),(sx,20.0,3.9), WHITEE)
    box(f"SideFrame_{s}", (2.9,0.35,6.0),(sx,20.2,3.9), GOLDEM)
    cyl(f"Emblem_{s}", 0.7,0.15,(sx,19.7,4.0), GOLD, rot=(math.radians(90),0,0))
# speaker stacks at stage corners
for s,sx in ((0,-9.3),(1,9.3)):
    box(f"Spk_{s}a",(0.9,0.9,1.3),(sx,15.0,1.75),BLACK)
    box(f"Spk_{s}b",(0.9,0.9,1.0),(sx,15.0,2.9),BLACK)
# centre steps down front of stage
for k in range(3):
    box(f"Step_{k}",(4.0,0.5,0.34),(0,14.0-k*0.5,0.17+ (2-k)*0.34),WHITE)
# hedge planters + greenery along stage front
for j,xx in enumerate(range(-8,9,2)):
    box(f"Hedge_{j}",(1.6,0.7,0.8),(xx,13.9,0.4),GREEN)
# lectern (stage left)
box("Lectern_b",(0.9,0.7,1.15),(-5.5,16.2,0.575+1.0),WHITE)
box("Lectern_s",(0.75,0.08,0.7),(-5.5,15.86,1.85),LEDBLU)

# ---------- truss + moving lights over stage ----------
for j,yy in enumerate((14.4,20.4)):
    box(f"Truss_{j}",(19,0.35,0.35),(0,yy,8.4),BLACK)
for k,(xx,yy) in enumerate([(-9,14.4),(9,14.4),(-9,20.4),(9,20.4)]):
    box(f"TrussLeg_{k}",(0.35,0.35,8.4),(xx,yy,4.2),BLACK)
for m_i in range(11):
    xx = -9 + m_i*1.8
    box(f"Mover_{m_i}",(0.32,0.32,0.5),(xx,14.4,7.9),(GOLDEM if m_i%2 else LEDCYN))

# ---------- runway ----------
box("Runway",     (2.8,14,0.42),(0,7,0.21), WHITE)
box("Runway_top", (2.8,14,0.04),(0,7,0.44), WHITE)
box("Runway_strip",(0.25,14,0.02),(0,7,0.47),WHITEE)

# ---------- round tables + chairs + centerpieces ----------
def table(tag, x, y):
    cyl(f"Tbl_{tag}", 0.95,0.78,(x,y,0.39), LINEN)
    cyl(f"Ctr_{tag}", 0.14,0.5,(x,y,1.05), GOLD)
    sph(f"Cndl_{tag}",0.12,(x,y,1.4), CANDLE)
    for c in range(8):
        a = math.radians(c*45)
        cx,cy = x+1.35*math.cos(a), y+1.35*math.sin(a)
        box(f"Seat_{tag}_{c}",(0.42,0.42,0.08),(cx,cy,0.5),SUIT)
        bx,by = x+1.6*math.cos(a), y+1.6*math.sin(a)
        box(f"Back_{tag}_{c}",(0.42,0.42,0.5),(bx,by,0.72),SUIT,rot=(0,0,a))
tt=0
for side in (-1,1):
    for ci,cx in enumerate((2.9,5.7,8.5)):
        for ri,ry in enumerate((2.0,5.3,8.6,11.6)):
            table(f"{tt}", side*cx, ry); tt+=1

# ---------- exhibition booths both walls (illuminated white frames) ----------
def booth(tag, x, y, inward):
    # inward = +1 faces +x (left wall), -1 faces -x (right wall)
    box(f"Bth_frame_{tag}",(0.25,3.4,3.6),(x,y,1.8),WHITEE)     # tall glowing frame
    box(f"Bth_head_{tag}", (0.3,3.4,0.35),(x,y,3.55),GOLDEM)    # gold header
    box(f"Bth_back_{tag}", (0.15,3.2,3.0),(x+0.25*inward,y,1.6),WHITE)
    box(f"Bth_screen_{tag}",(0.08,1.6,1.4),(x+0.5*inward,y,2.1),LEDBLU)
    box(f"Bth_counter_{tag}",(0.9,2.4,1.0),(x+1.1*inward,y,0.5),WHITE)
    box(f"Bth_plinth_{tag}",(0.5,0.5,1.1),(x+1.0*inward,y-0.9,0.55),GOLD)
    box(f"Bth_glow_{tag}",  (0.9,2.4,0.06),(x+1.1*inward,y,1.03),WHITEE)
for i,yy in enumerate((-4.0,0.2,4.4,8.6,12.4)):
    booth(f"L{i}", -13.8, yy, +1)
    booth(f"R{i}",  13.8, yy, -1)

# ---------- gold WELCOME entrance arch over runway (front) ----------
ay=-12.0
box("Arch_postL",(0.8,0.9,3.4),(-2.9,ay,1.7),GOLD)
box("Arch_postR",(0.8,0.9,3.4),( 2.9,ay,1.7),GOLD)
box("Arch_top",  (7.4,0.9,0.9),(0,ay,3.6),GOLD)
box("Arch_inner",(6.2,0.4,0.5),(0,ay,3.3),GOLDEM)
cyl("Arch_medL",0.4,0.12,(-2.4,ay-0.5,1.6),GOLD,rot=(math.radians(90),0,0))
cyl("Arch_medR",0.4,0.12,( 2.4,ay-0.5,1.6),GOLD,rot=(math.radians(90),0,0))
# 3D WELCOME text
bpy.ops.object.text_add(location=(0,ay-0.55,3.55))
tx=bpy.context.active_object; tx.name="WelcomeText"
tx.data.body="WELCOME"; tx.data.size=0.62; tx.data.extrude=0.04; tx.data.align_x='CENTER'
tx.rotation_euler=(math.radians(90),0,0); tx.data.materials.append(GOLDEM)
bpy.ops.object.convert(target='MESH')
box("Carpet_run",(2.8,7,0.03),(0,-8.5,0.03),WHITE)

# ---------- LEFT foreground: photo booth + reception + cocktail ----------
# photo booth (black drape + gold arch + ring lights)
box("Photo_drape",(4,0.3,3.4),(-12,-15,1.7),BLACK)
box("Photo_archL",(0.35,0.35,3.0),(-13.6,-14.2,1.5),GOLD)
box("Photo_archR",(0.35,0.35,3.0),(-10.4,-14.2,1.5),GOLD)
box("Photo_archT",(3.6,0.35,0.35),(-12,-14.2,3.0),GOLD)
cyl("Ring1",0.5,0.08,(-13.6,-13.4,2.4),WHITEE,rot=(math.radians(90),0,0))
cyl("Ring2",0.5,0.08,(-10.4,-13.4,2.4),WHITEE,rot=(math.radians(90),0,0))
# reception / registration curved desk
box("Recept_a",(3.2,1.0,1.1),(-9,-11,0.55),WHITE)
box("Recept_glow",(3.2,0.1,0.9),(-9,-10.45,0.85),LEDBLU)
box("Recept_screen",(0.9,0.1,1.4),(-11,-11,1.8),LEDBLU,rot=(0,0,math.radians(20)))
# cocktail poseur tables + stools
for i,(px,py) in enumerate([(-6,-16),(-4.4,-14.8),(-6.2,-13.6),(-4.2,-16.4)]):
    cyl(f"Poseur_stem_{i}",0.12,1.1,(px,py,0.55),WHITE)
    cyl(f"Poseur_top_{i}",0.45,0.06,(px,py,1.12),WHITE)

# ---------- RIGHT foreground: lounge + catering bar ----------
box("Lounge_rug",(5.5,4.5,0.02),(10,-14,0.02),BLACK)
box("Sofa_1",(3.0,1.0,0.85),(10,-15.6,0.45),SOFA)
box("Sofa_2",(3.0,1.0,0.85),(10,-12.4,0.45),SOFA,rot=(0,0,math.radians(180)))
box("Sofa_1b",(3.0,0.4,0.5),(10,-16.0,0.9),SOFA)
box("Sofa_2b",(3.0,0.4,0.5),(10,-12.0,0.9),SOFA)
box("Coffee",(1.6,1.0,0.4),(10,-14,0.2),WOOD)
for i,(px,py) in enumerate([(7.6,-16.4),(12.4,-16.4),(7.6,-11.6)]):
    cyl(f"Plant_pot_{i}",0.35,0.6,(px,py,0.3),WHITE)
    sph(f"Plant_top_{i}",0.7,(px,py,1.1),GREEN)
# catering / buffet bar
box("Bar_counter",(6.0,1.2,1.05),(13,-8,0.525),WOOD)
box("Bar_glow",(6.0,0.08,0.9),(13,-8.62,0.75),GOLDEM)
box("Bar_shelf",(6.0,0.4,2.2),(14.6,-8,1.6),BLACK,rot=(0,math.radians(0),0))
for i in range(10):
    bx = 10.6+i*0.55
    cyl(f"Bottle_{i}",0.09,0.5,(bx if bx<15 else 14.9,-8.1,1.2+ (0.9 if i%2 else 0.0)),(REDG if i%3 else AMBER))
for i in range(6):
    cyl(f"Tray_{i}",0.35,0.12,(10.7+i*0.7,-7.6,1.12),WHITE)
cyl("Chafing",0.4,0.35,(13.6,-7.6,1.28),GOLD)

# ---------- a few people (simple figures, for scale) ----------
def person(tag,x,y,rot=0.0):
    cyl(f"Body_{tag}",0.2,1.15,(x,y,0.62),SUIT,verts=10)
    sph(f"Head_{tag}",0.14,(x,y,1.35),SKIN)
for i,(px,py) in enumerate([(-3,-9),(-9.2,-12),(3.5,-10),(13,-9.2),(9.5,-13.5),(-6,-15.2),(1,-3),(-2,4)]):
    person(i,px,py)

# ---------- chandeliers (front bays) ----------
for i,(px,py) in enumerate([(-9,-4),(9,-4)]):
    cyl(f"Chand_{i}",1.1,0.25,(px,py,7.6),GOLDEM)

# ---------- lighting (so .blend/render open ready) ----------
bpy.ops.object.light_add(type='SUN', location=(10,-24,26)); bpy.context.active_object.data.energy=1.6
def area(name,loc,size,energy,color):
    bpy.ops.object.light_add(type='AREA',location=loc); L=bpy.context.active_object
    L.name=name; L.data.size=size; L.data.energy=energy; L.data.color=color
area("Key_warm",(0,4,9),22,900,(1.0,0.8,0.55))
area("Fill_blue",(0,17,8),14,700,(0.4,0.6,1.0))
area("Front_fill",(0,-10,8),16,500,(1.0,0.85,0.7))
def spot(name,loc,tgt,energy,color):
    bpy.ops.object.light_add(type='SPOT',location=loc); L=bpy.context.active_object
    L.name=name; L.data.energy=energy; L.data.spot_size=math.radians(45); L.data.color=color
    dx,dy,dz=tgt[0]-loc[0],tgt[1]-loc[1],tgt[2]-loc[2]
    L.rotation_euler=(math.atan2(math.hypot(dx,dy),-dz)+math.pi, 0, math.atan2(dy,dx)-math.pi/2)
for i,xx in enumerate((-6,-2,2,6)):
    spot(f"Spot_{i}",(xx,14.4,7.7),(xx*0.5,18,1.2),1500,((0.95,0.75,0.3) if i%2 else (0.4,0.6,1.0)))

# world
scn.world = bpy.data.worlds.new("W"); scn.world.use_nodes=True
bg=scn.world.node_tree.nodes.get("Background")
if bg: bg.inputs[0].default_value=(0.006,0.008,0.02,1); bg.inputs[1].default_value=0.25

# ---------- cameras (two framings to match the references) ----------
bpy.ops.object.camera_add(location=(0,-30,21), rotation=(math.radians(62),0,0))
cam_iso=bpy.context.active_object; cam_iso.name="CAM_ISO"; cam_iso.data.lens=20
bpy.ops.object.camera_add(location=(-8.8,6.2,1.7))
cam_stage=bpy.context.active_object; cam_stage.name="CAM_STAGE"; cam_stage.data.lens=20
aim(cam_stage,(1.5,19.6,3.1))
scn.camera=cam_iso

# ---------- export ----------
out = os.environ.get("ZYNTH_3D_OUT", os.path.join(os.getcwd(), "zynth_3d_out"))
os.makedirs(out, exist_ok=True)
n_obj=len([o for o in bpy.data.objects if o.type=='MESH'])
base=f"{out}/AURUM_Novotel_Event_v2"
try: bpy.ops.export_scene.gltf(filepath=base+".glb", export_format='GLB'); print("GLB ok")
except Exception as e: print("GLB fail", e)
try: bpy.ops.export_scene.fbx(filepath=base+".fbx"); print("FBX ok")
except Exception as e: print("FBX fail", e)
try: bpy.ops.wm.save_as_mainfile(filepath=base+".blend"); print("BLEND ok")
except Exception as e: print("BLEND fail", e)
print("MESH_OBJECTS", n_obj)
