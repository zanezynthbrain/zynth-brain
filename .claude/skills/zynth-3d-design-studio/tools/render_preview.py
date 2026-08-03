import bpy, os
bpy.ops.wm.open_mainfile(filepath=os.environ.get("ZYNTH_3D_BLEND", os.path.join(os.getcwd(),"zynth_3d_out","AURUM_Novotel_Event_Stage.blend")))
scn = bpy.context.scene
scn.render.engine = 'CYCLES'
try:
    scn.cycles.device = 'CPU'
    scn.cycles.samples = 24
except Exception as e:
    print("cyc cfg", e)
scn.render.resolution_x = 1600; scn.render.resolution_y = 900
if not scn.world:
    scn.world = bpy.data.worlds.new("W")
scn.world.use_nodes = True
bg = scn.world.node_tree.nodes.get("Background")
if bg: bg.inputs[0].default_value = (0.01,0.01,0.02,1); bg.inputs[1].default_value = 0.4
scn.render.filepath = os.environ.get("ZYNTH_3D_PREVIEW", os.path.join(os.getcwd(),"zynth_3d_out","AURUM_preview.png"))
bpy.ops.render.render(write_still=True); print("RENDER OK")
