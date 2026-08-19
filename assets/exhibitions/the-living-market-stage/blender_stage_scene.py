import bpy, math
from mathutils import Vector
from pathlib import Path

OUT=Path('/home/ubuntu/zynth_exhibition/blender_stage_output'); OUT.mkdir(parents=True, exist_ok=True)
# clean
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    pass

# materials
def mat(name, color, metallic=0.0, rough=0.45, emission=None):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*emission,1); bs.inputs['Emission Strength'].default_value=4.0
    return m
navy=mat('ZYNTH Navy',(0.025,0.12,0.16),.3,.3)
gold=mat('Market Gold',(0.82,0.52,0.12),.5,.27)
teal=mat('Living Teal',(0.06,0.40,0.42),.15,.32)
coral=mat('Clay Coral',(0.72,0.18,0.10),.1,.42)
cream=mat('Paper Cream',(0.86,0.82,0.70),0,.6)
black=mat('Stage Black',(0.008,0.01,0.012),.1,.25)
led=mat('LED Content',(0.05,0.32,0.38),.1,.2,emission=(0.03,0.35,0.4))
white=mat('Lighting White',(0.95,0.95,0.9),0,.25,emission=(1,1,0.9))

# collections
def coll(name): return bpy.data.collections.new(name)
root=bpy.context.scene.collection
cols={n:coll(n) for n in ['01_STAGE','02_AV','03_BRANDING','04_LIGHTING','05_AUDIENCE','06_BACKSTAGE','07_PROPS']}
for c in cols.values(): root.children.link(c)

def move_to(obj, c):
    for cc in list(obj.users_collection): cc.objects.unlink(obj)
    c.objects.link(obj)

def cube(name, loc, scale, material, c, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=name; o.scale=(scale[0]/2,scale[1]/2,scale[2]/2); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=bevel; mod.segments=3
    o.data.materials.append(material); move_to(o,c); return o

def cyl(name, loc, radius, depth, material, c):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(material); move_to(o,c); return o

def text(name, body, loc, size, material, c, rot=(math.pi/2,0,0), align='CENTER'):
    bpy.ops.object.text_add(location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.data.body=body; o.data.align_x=align; o.data.align_y='CENTER'; o.data.size=size; o.data.extrude=.012; o.data.bevel_depth=.004; o.data.materials.append(material); move_to(o,c); return o

# Stage dimensions: 18m wide x 8m deep, 1.2m high
cube('Stage Platform',(0,0,0.6),(18,8,1.2),black,cols['01_STAGE'],.15)
cube('Stage Fascia',(0,-4.02,0.7),(18,.12,.8),gold,cols['03_BRANDING'],.03)
# central portal / stage frame
cube('Portal Left',(-7.8,1.0,5.0),(.35,.35,8),gold,cols['01_STAGE'],.05)
cube('Portal Right',(7.8,1.0,5.0),(.35,.35,8),gold,cols['01_STAGE'],.05)
cube('Portal Top',(0,1.0,8.85),(16,.35,.35),gold,cols['01_STAGE'],.05)
# LED wall and side ribbons
cube('Main LED Wall',(0,2.0,5.0),(11.5,.25,5.4),led,cols['02_AV'],.03)
cube('Left Vertical LED',(-6.35,2.0,4.5),(1.5,.22,5.0),teal,cols['02_AV'],.02)
cube('Right Vertical LED',(6.35,2.0,4.5),(1.5,.22,5.0),teal,cols['02_AV'],.02)
# layered set fins
for i,x in enumerate([-5.0,-3.7,3.7,5.0]): cube(f'Brand Fin {i}',(x,1.4,3.6),(0.18,.18,5.5),coral if i%2==0 else gold,cols['03_BRANDING'],.02)
# center market spine / hero sculpture
cyl('Hero Totem',(0,-.2,2.5),1.15,5.0,gold,cols['03_BRANDING'])
for i in range(4):
    a=math.radians(45+i*90); x=math.cos(a)*1.45; y=-.2+math.sin(a)*1.45
    cube(f'Spine Ray {i}',(x,y,2.5),(2.2,.12,.12),coral if i%2 else teal,cols['03_BRANDING'],.02).rotation_euler[2]=a
text('Stage Title','THE LIVING MARKET',(0,1.72,5.0),.68,cream,cols['03_BRANDING'],rot=(math.pi/2,0,0))
text('Stage Subtitle','FROM LOCAL ROOTS TO NEXT-GEN GROWTH',(0,1.69,4.25),.22,gold,cols['03_BRANDING'],rot=(math.pi/2,0,0))
text('Front Fascia','ZYNTH AI AGENCY',(0,-4.10,.75),.38,navy,cols['03_BRANDING'],rot=(math.pi/2,0,0))
# presenter desk + demo plinths
cube('Presenter Deck',(0,-1.25,1.35),(5.4,2.0,.18),gold,cols['01_STAGE'],.04)
cyl('Demo Plinth L',(-4.0,-.8,1.55),.65,.55,teal,cols['07_PROPS'])
cyl('Demo Plinth R',(4.0,-.8,1.55),.65,.55,coral,cols['07_PROPS'])
# stairs and ramps
for i in range(4): cube(f'Left Stair {i}',(-5.0,-3.3+i*.4,.2+i*.18),(2.2,.4,.2+i*.18),cream,cols['01_STAGE'],.03)
for i in range(4): cube(f'Right Stair {i}',(5.0,-3.3+i*.4,.2+i*.18),(2.2,.4,.2+i*.18),cream,cols['01_STAGE'],.03)
# audience risers and seating blocks
for row in range(4):
    y=-7.0-row*1.55; h=.25+row*.15
    cube(f'Audience Riser {row}',(0,y,h/2),(15,1.0,h),navy,cols['05_AUDIENCE'],.04)
    for x in [-6,-4.5,-3,-1.5,0,1.5,3,4.5,6]: cyl(f'Seat {row}_{x}',(x,y-.1,h+.22),.16,.38,gold,cols['05_AUDIENCE'])
# backstage/service block
cube('Backstage Service Wall',(0,4.5,2.0),(16,.5,4),black,cols['06_BACKSTAGE'])
text('Backstage Label','BACKSTAGE / GREEN ROOM / TECH',(0,4.18,2.1),.25,cream,cols['06_BACKSTAGE'],rot=(math.pi/2,0,0))
# overhead lighting bars
for x in [-5,0,5]:
    bar=cube(f'Lighting Bar {x}',(x,-.2,9.2),(3.8,.18,.18),black,cols['04_LIGHTING']);
    for j in range(4):
        cyl(f'Fresnel {x}_{j}',(x-1.4+j*.9,-.35,8.8),.11,.55,white,cols['04_LIGHTING']).rotation_euler[0]=math.pi/2
# area lights
def area(name, loc, energy, color, size, target=(0,0,0)):
    data=bpy.data.lights.new(name,'AREA'); data.energy=energy; data.color=color; data.shape='DISK'; data.size=size; o=bpy.data.objects.new(name,data); cols['04_LIGHTING'].objects.link(o); o.location=loc
    direction=Vector(target)-o.location; o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); return o
area('Key Light',(-5,-5,8),1500,(1.0,.75,.55),5,(0,0,2))
area('Fill Light',(5,-3,7),1200,(.45,.75,1.0),4,(0,0,2))
area('Back Light',(0,4,8),1000,(.2,1,.85),4,(0,1,4))
# camera
bpy.ops.object.camera_add(location=(23,-28,18)); cam=bpy.context.object; cam.name='Camera_Hero'; direction=Vector((0,0,3))-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.lens=42; bpy.context.scene.camera=cam
# render settings
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1400; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False; scene.world.color=(.015,.02,.025)
# metadata
scene['design_title']='The Living Market — Main Stage'; scene['venue_assumption']='Yangon Convention Centre; dimensions subject to venue survey'; scene['stage_width_m']=18.0; scene['stage_depth_m']=8.0; scene['stage_height_m']=1.2; scene['design_status']='Concept blockout for client review; engineering validation required'
# save and render
scene.render.filepath=str(OUT/'stage_hero.png'); bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ZYNTH_The_Living_Market_Main_Stage.blend')); bpy.ops.render.render(write_still=True)
# second view
cam.location=(-19,-24,12); direction=Vector((0,0,3))-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); scene.render.filepath=str(OUT/'stage_reverse.png'); bpy.ops.render.render(write_still=True)
# overhead
cam.location=(0,-.5,28); direction=Vector((0,0,0))-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.lens=52; scene.render.filepath=str(OUT/'stage_plan.png'); bpy.ops.render.render(write_still=True)
# save final with hero camera
cam.location=(23,-28,18); direction=Vector((0,0,3))-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.lens=42; bpy.context.scene.camera=cam; bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ZYNTH_The_Living_Market_Main_Stage.blend'))
print('Saved Blender stage package to',OUT)
