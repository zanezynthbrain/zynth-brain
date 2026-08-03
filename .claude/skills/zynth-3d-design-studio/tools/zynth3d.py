"""ZYNTH 3D core library — headless Blender (bpy) building blocks for detailed,
vision-proof 3D design. Import this from any scene script.

Why this exists: raw primitives read as a *sketch*. Detail comes from five levers,
all offline-capable (no asset downloads needed):

  1. BEVEL every hard edge      -> edges catch light, kills the CG-plastic look
  2. REAL geometry, instanced   -> a chair that is a chair, duplicated cheaply
  3. PROCEDURAL PBR materials   -> carpet nap, wood grain, brushed metal, marble
  4. VOLUMETRIC haze + spots    -> visible light beams (the #1 "event render" cue)
  5. AgX tonemap + DOF + lens   -> photographic response instead of blown highlights

Everything here is offline. If you later run this on a machine WITH network, swap
`m_*` procedural materials for real PBR maps (PolyHaven / BlenderKit / Quixel) via
`m_textured()` — the texture slots are already wired for it.

Usage:
    import zynth3d as z
    z.new_scene(); z.set_render(samples=64)
    gold = z.m_metal_brushed("Gold", (0.83,0.65,0.22), rough=0.28)
    chair = z.prefab_banquet_chair(gold)
    z.place(chair, (1,2,0), rot_z=0.7)
"""
import bpy, math, os, random
import numpy as np

# ----------------------------------------------------------------------------
# scene / render
# ----------------------------------------------------------------------------

def new_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def set_render(engine="CYCLES", samples=64, res=(1600, 900), exposure=0.0,
               look="None", transparent=False):
    """Cycles CPU + AgX. EEVEE needs a GPU/EGL context, unavailable headless."""
    scn = bpy.context.scene
    scn.render.engine = engine
    if engine == "CYCLES":
        scn.cycles.device = "CPU"
        scn.cycles.samples = samples
        scn.cycles.use_denoising = True
        scn.cycles.max_bounces = 8
        scn.cycles.transmission_bounces = 4
        scn.cycles.volume_step_rate = 4.0      # cheaper volumetrics
        scn.cycles.volume_max_steps = 128
    scn.render.resolution_x, scn.render.resolution_y = res
    scn.render.film_transparent = transparent
    # photographic response — the single biggest fix for blown-out LED walls
    for vt in ("AgX", "Filmic", "Standard"):
        try:
            scn.view_settings.view_transform = vt
            break
        except Exception:
            continue
    try:
        scn.view_settings.look = look
    except Exception:
        pass
    scn.view_settings.exposure = exposure
    return scn


# ----------------------------------------------------------------------------
# material helpers — node graph plumbing
# ----------------------------------------------------------------------------

def _newmat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree, m.node_tree.nodes, m.node_tree.links


def _bsdf(nodes):
    return nodes.get("Principled BSDF")


def _set(node, keys, val):
    """Set the first input that exists — input names move between Blender versions."""
    for k in keys:
        if k in node.inputs:
            node.inputs[k].default_value = val
            return True
    return False


def _base(b, color, metallic=0.0, rough=0.6, spec=None, sheen=None, ior=None):
    _set(b, ["Base Color"], (*color, 1))
    _set(b, ["Metallic"], metallic)
    _set(b, ["Roughness"], rough)
    if spec is not None:
        _set(b, ["Specular IOR Level", "Specular"], spec)
    if sheen is not None:
        _set(b, ["Sheen Weight", "Sheen"], sheen)
    if ior is not None:
        _set(b, ["IOR"], ior)


def _bump(nt, nodes, links, b, src_out, strength=0.2, distance=0.02):
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    links.new(src_out, bump.inputs["Height"])
    if "Normal" in b.inputs:
        links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return bump


def _noise(nodes, scale=50.0, detail=8.0, rough=0.55, dist=0.0):
    n = nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    if "Roughness" in n.inputs:
        n.inputs["Roughness"].default_value = rough
    if "Distortion" in n.inputs:
        n.inputs["Distortion"].default_value = dist
    return n


def _ramp(nodes, stops):
    """stops = [(pos, (r,g,b,a)), ...]"""
    r = nodes.new("ShaderNodeValToRGB")
    el = r.color_ramp.elements
    while len(el) > 1:
        el.remove(el[-1])
    el[0].position, el[0].color = stops[0]
    for pos, col in stops[1:]:
        e = el.new(pos)
        e.color = col
    return r


def _mapping(nodes, links, scale=(1, 1, 1)):
    """Object-coordinate mapping — keeps texture scale stable regardless of UVs."""
    co = nodes.new("ShaderNodeTexCoord")
    mp = nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    links.new(co.outputs["Object"], mp.inputs["Vector"])
    return mp


# ----------------------------------------------------------------------------
# procedural PBR materials
# ----------------------------------------------------------------------------

def m_plain(name, color, metallic=0.0, rough=0.6, sheen=None):
    m, nt, nodes, links = _newmat(name)
    _base(_bsdf(nodes), color, metallic, rough, sheen=sheen)
    return m


def m_carpet(name, color, scale=320.0, bump=0.35, variation=0.10):
    """Dense fibre nap + slow tonal drift. Reads as carpet, not painted concrete."""
    m, nt, nodes, links = _newmat(name)
    b = _bsdf(nodes)
    _base(b, color, 0.0, 0.96, sheen=0.15)
    fib = _noise(nodes, scale=scale, detail=10.0, rough=0.7)
    _bump(nt, nodes, links, b, fib.outputs["Fac"], strength=bump, distance=0.006)
    drift = _noise(nodes, scale=3.5, detail=3.0)
    r = _ramp(nodes, [(0.35, (*[c * (1 - variation) for c in color], 1)),
                      (0.70, (*[min(1, c * (1 + variation)) for c in color], 1))])
    links.new(drift.outputs["Fac"], r.inputs["Fac"])
    links.new(r.outputs["Color"], b.inputs["Base Color"])
    return m


def m_wood(name, dark=(0.13, 0.075, 0.035), light=(0.30, 0.19, 0.09),
           grain=14.0, distortion=2.2, rough=0.42):
    """Wave texture warped by noise = plank grain. Classic, cheap, convincing."""
    m, nt, nodes, links = _newmat(name)
    b = _bsdf(nodes)
    _base(b, light, 0.0, rough, spec=0.5)
    mp = _mapping(nodes, links, scale=(1, 1, 1))
    w = nodes.new("ShaderNodeTexWave")
    w.wave_type = "BANDS"
    w.bands_direction = "Z"
    w.wave_profile = "SIN"
    w.inputs["Scale"].default_value = grain
    w.inputs["Distortion"].default_value = distortion
    w.inputs["Detail"].default_value = 6.0
    links.new(mp.outputs["Vector"], w.inputs["Vector"])
    r = _ramp(nodes, [(0.25, (*dark, 1)), (0.75, (*light, 1))])
    links.new(w.outputs["Fac"], r.inputs["Fac"])
    links.new(r.outputs["Color"], b.inputs["Base Color"])
    rr = _ramp(nodes, [(0.3, (rough - 0.10,) * 3 + (1,)), (0.8, (rough + 0.12,) * 3 + (1,))])
    links.new(w.outputs["Fac"], rr.inputs["Fac"])
    links.new(rr.outputs["Color"], b.inputs["Roughness"])
    _bump(nt, nodes, links, b, w.outputs["Fac"], strength=0.12, distance=0.004)
    return m


def m_metal_brushed(name, color, rough=0.28, streak=0.9):
    """Stretched noise into roughness = brushed/anisotropic metal, not mirror-chrome."""
    m, nt, nodes, links = _newmat(name)
    b = _bsdf(nodes)
    _base(b, color, 1.0, rough)
    mp = _mapping(nodes, links, scale=(1.0, 260.0, 1.0))  # stretched along one axis
    n = _noise(nodes, scale=1.0, detail=6.0)
    links.new(mp.outputs["Vector"], n.inputs["Vector"])
    r = _ramp(nodes, [(0.35, (max(0.02, rough - 0.12),) * 3 + (1,)),
                      (0.75, (min(1.0, rough + 0.14 * streak),) * 3 + (1,))])
    links.new(n.outputs["Fac"], r.inputs["Fac"])
    links.new(r.outputs["Color"], b.inputs["Roughness"])
    return m


def m_marble(name, base=(0.045, 0.05, 0.075), vein=(0.55, 0.52, 0.48),
             scale=2.2, rough=0.08):
    """Polished stone floor — the reflection is what sells an event render."""
    m, nt, nodes, links = _newmat(name)
    b = _bsdf(nodes)
    _base(b, base, 0.0, rough, spec=0.6)
    mp = _mapping(nodes, links, scale=(1, 1, 1))
    n = _noise(nodes, scale=scale, detail=10.0, rough=0.6, dist=6.0)
    links.new(mp.outputs["Vector"], n.inputs["Vector"])
    r = _ramp(nodes, [(0.42, (*base, 1)), (0.50, (*vein, 1)), (0.58, (*base, 1))])
    links.new(n.outputs["Fac"], r.inputs["Fac"])
    links.new(r.outputs["Color"], b.inputs["Base Color"])
    return m


def m_fabric(name, color, scale=180.0, sheen=0.6, rough=0.85, bump=0.25):
    """Velvet / linen / drape. Sheen is what makes cloth read as cloth."""
    m, nt, nodes, links = _newmat(name)
    b = _bsdf(nodes)
    _base(b, color, 0.0, rough, sheen=sheen)
    n = _noise(nodes, scale=scale, detail=6.0)
    _bump(nt, nodes, links, b, n.outputs["Fac"], strength=bump, distance=0.004)
    return m


def m_emissive(name, color, strength=3.0, base=None):
    m, nt, nodes, links = _newmat(name)
    b = _bsdf(nodes)
    _base(b, base or [c * 0.25 for c in color], 0.0, 0.5)
    _set(b, ["Emission Color", "Emission"], (*color, 1))
    _set(b, ["Emission Strength"], strength)
    return m


def m_led_screen(name, image, strength=2.0, px=(260, 68), pixel_depth=0.45,
                 tint=(1.0, 1.0, 1.0)):
    """Image emission modulated by an aspect-correct pixel grid, driven by UVs.
    Use with curved_screen()/z.box() surfaces that actually have a UV map —
    without UVs the texture repeats per-object and reads as vertical stripes.
    `px` = visible LED cells across (u, v)."""
    m, nt, nodes, links = _newmat(name)
    b = _bsdf(nodes)
    _base(b, (0.010, 0.010, 0.012), 0.0, 0.34)
    uv = nodes.new("ShaderNodeUVMap")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.extension = "EXTEND"
    links.new(uv.outputs["UV"], tex.inputs["Vector"])
    grid_map = nodes.new("ShaderNodeMapping")
    grid_map.inputs["Scale"].default_value = (px[0], px[1], 1.0)
    links.new(uv.outputs["UV"], grid_map.inputs["Vector"])
    grid = nodes.new("ShaderNodeTexChecker")
    grid.inputs["Scale"].default_value = 1.0
    grid.inputs["Color1"].default_value = (1, 1, 1, 1)
    grid.inputs["Color2"].default_value = (1 - pixel_depth,) * 3 + (1,)
    links.new(grid_map.outputs["Vector"], grid.inputs["Vector"])
    mix = nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    links.new(tex.outputs["Color"], mix.inputs[6])
    links.new(grid.outputs["Color"], mix.inputs[7])
    tintn = nodes.new("ShaderNodeMix")
    tintn.data_type = "RGBA"
    tintn.blend_type = "MULTIPLY"
    tintn.inputs["Factor"].default_value = 1.0
    links.new(mix.outputs[2], tintn.inputs[6])
    tintn.inputs[7].default_value = (*tint, 1)
    for k in ("Emission Color", "Emission"):
        if k in b.inputs:
            links.new(tintn.outputs[2], b.inputs[k])
            break
    _set(b, ["Emission Strength"], strength)
    return m


def m_glass(name, color=(0.9, 0.93, 0.95), rough=0.03):
    m, nt, nodes, links = _newmat(name)
    b = _bsdf(nodes)
    _base(b, color, 0.0, rough, ior=1.45)
    _set(b, ["Transmission Weight", "Transmission"], 1.0)
    return m


def m_textured(name, folder, rough_default=0.5):
    """HOOK for when you run this on a networked machine: point at a PolyHaven /
    Quixel folder containing *_diff/_nor/_rough maps and it wires them up.
    Offline here, so it degrades gracefully to a plain material."""
    m, nt, nodes, links = _newmat(name)
    b = _bsdf(nodes)
    _base(b, (0.5, 0.5, 0.5), 0.0, rough_default)
    if not folder or not os.path.isdir(folder):
        return m
    got = {}
    for f in sorted(os.listdir(folder)):
        low = f.lower()
        for key, tags in (("diff", ("diff", "albedo", "basecolor", "_col")),
                          ("rough", ("rough", "_rgh")),
                          ("nor", ("nor", "normal"))):
            if key not in got and any(t in low for t in tags):
                got[key] = os.path.join(folder, f)
    if "diff" in got:
        t = nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(got["diff"])
        links.new(t.outputs["Color"], b.inputs["Base Color"])
    if "rough" in got:
        t = nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(got["rough"])
        t.image.colorspace_settings.name = "Non-Color"
        links.new(t.outputs["Color"], b.inputs["Roughness"])
    if "nor" in got:
        t = nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(got["nor"])
        t.image.colorspace_settings.name = "Non-Color"
        nm = nodes.new("ShaderNodeNormalMap")
        links.new(t.outputs["Color"], nm.inputs["Color"])
        if "Normal" in b.inputs:
            links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


# ----------------------------------------------------------------------------
# generated screen content (numpy -> bpy.Image, no network, no PIL)
# ----------------------------------------------------------------------------

def make_led_content(name="LEDContent", w=1024, h=512,
                     deep=(0.02, 0.09, 0.34), mid=(0.06, 0.26, 0.72),
                     gold=(1.0, 0.78, 0.32), swooshes=3, emblem=True):
    """Paint a brand LED loop: deep-blue field, radial core glow, gold arc swooshes,
    optional centre emblem. Returns a bpy Image usable by m_led_screen."""
    yy, xx = np.mgrid[0:h, 0:w]
    u = xx / (w - 1.0)
    v = yy / (h - 1.0)
    cx, cy = 0.5, 0.52
    ar = w / float(h)
    d = np.sqrt(((u - cx) * ar) ** 2 + (v - cy) ** 2)

    img = np.zeros((h, w, 3), dtype=np.float32)
    for i, c in enumerate(deep):
        img[..., i] = c
    core = np.exp(-(d ** 2) / (2 * 0.20 ** 2))          # centre glow
    for i in range(3):
        img[..., i] += (mid[i] - deep[i]) * core
    halo = np.exp(-(d ** 2) / (2 * 0.55 ** 2)) * 0.35
    for i in range(3):
        img[..., i] += mid[i] * halo * 0.6

    # gold arc swooshes — concentric bands with soft falloff
    rng = np.random.default_rng(11)
    for s in range(swooshes):
        r0 = 0.26 + 0.13 * s
        thick = 0.020 + 0.008 * s
        band = np.exp(-((d - r0) ** 2) / (2 * thick ** 2))
        ang = np.arctan2(v - cy, (u - cx) * ar)
        mask = (np.cos(ang * 1.0 + s * 2.1) * 0.5 + 0.5) ** 2.2   # fade around the arc
        gainmap = band * mask * (0.85 - 0.16 * s)
        for i in range(3):
            img[..., i] += gold[i] * gainmap
        # sparkle grain riding the arc (the "gold dust" look)
        spark = (rng.random((h, w)) > 0.9975).astype(np.float32)
        spark = spark * band * 2.2
        for i in range(3):
            img[..., i] += gold[i] * spark

    # thin horizon light-streak
    streak = np.exp(-((v - 0.63) ** 2) / (2 * 0.010 ** 2)) * 0.55
    for i in range(3):
        img[..., i] += mid[i] * streak

    if emblem:
        e = np.exp(-((d - 0.085) ** 2) / (2 * 0.030 ** 2))
        e *= (np.abs(np.cos(np.arctan2(v - cy, (u - cx) * ar) * 3.0)) ** 1.5)
        for i in range(3):
            img[..., i] += gold[i] * e * 1.5

    img = np.clip(img, 0.0, 4.0)
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = img
    bi = bpy.data.images.new(name, width=w, height=h, float_buffer=True)
    bi.pixels.foreach_set(rgba[::-1].ravel())   # Blender images are bottom-up
    bi.pack()
    return bi


# ----------------------------------------------------------------------------
# geometry primitives + detail
# ----------------------------------------------------------------------------

def box(name, dims, loc, mat=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = dims
    if mat:
        o.data.materials.append(mat)
    return o


def cyl(name, r, d, loc, mat=None, verts=32, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc,
                                        vertices=verts, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    if mat:
        o.data.materials.append(mat)
    return o


def sph(name, r, loc, mat=None, segs=24, rings=14):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc,
                                         segments=segs, ring_count=rings)
    o = bpy.context.active_object
    o.name = name
    if mat:
        o.data.materials.append(mat)
    return o


def torus(name, major, minor, loc, mat=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     location=loc, rotation=rot,
                                     major_segments=32, minor_segments=12)
    o = bpy.context.active_object
    o.name = name
    if mat:
        o.data.materials.append(mat)
    return o


def curved_screen(name, apex_y, radius, span_deg, height, z0, mat,
                  nu=64, nv=16, flip_u=False):
    """Single continuous curved LED surface with a proper UV map, so screen content
    maps across the WHOLE wall once instead of repeating per panel.

    Concave toward the audience (-Y): `apex_y` is the y of the screen CENTRE — its
    farthest point — and the wings wrap forward toward the viewer. Larger `radius`
    = gentler curve. Centre of curvature sits at y = apex_y - radius."""
    verts, faces, uvs = [], [], []
    half = math.radians(span_deg) / 2.0
    cy = apex_y - radius
    for j in range(nv + 1):
        vz = z0 + height * (j / nv)
        for i in range(nu + 1):
            t = i / nu
            phi = -half + t * (2 * half)
            verts.append((radius * math.sin(phi), cy + radius * math.cos(phi), vz))
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            bb = a + 1
            c = a + (nu + 1) + 1
            d = a + (nu + 1)
            faces.append((a, bb, c, d))
            u0, u1 = i / nu, (i + 1) / nu
            if flip_u:
                u0, u1 = 1 - u0, 1 - u1
            v0, v1 = j / nv, (j + 1) / nv
            uvs.extend([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    uvl = me.uv_layers.new(name="UVMap")
    for k, uv in enumerate(uvs):
        uvl.data[k].uv = uv
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    me.update()
    sel_only(o)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    smooth(o, angle=60.0)
    return o


def sel_only(objs):
    bpy.ops.object.select_all(action="DESELECT")
    objs = objs if isinstance(objs, (list, tuple)) else [objs]
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    return objs


def bevel(obj, width=0.012, segments=2, angle=50.0, apply=True):
    """The single highest-value detail pass. Real edges are never perfectly sharp."""
    sel_only(obj)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(angle)
    m.use_clamp_overlap = True
    m.harden_normals = False
    if apply:
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
        except Exception:
            pass
    return obj


def smooth(obj, angle=35.0):
    sel_only(obj)
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angle))
    except Exception:
        try:
            bpy.ops.object.shade_smooth()
        except Exception:
            pass
    return obj


def join(objs, name):
    objs = [o for o in objs if o and o.name in bpy.data.objects]
    sel_only(objs)
    if len(objs) > 1:
        bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = name
    return o


def place(src, loc, rot_z=0.0, rot=None, scale=None, name=None):
    """Linked duplicate — shares mesh data, so 200 chairs cost one chair of memory."""
    d = src.copy()          # object copy, data NOT copied => instanced
    bpy.context.collection.objects.link(d)
    d.location = loc
    d.rotation_euler = rot if rot else (0, 0, rot_z)
    if scale:
        d.scale = scale
    if name:
        d.name = name
    return d


def stash(obj, z=-500.0):
    """Park a prefab far below the floor so it never renders but stays instanceable."""
    obj.location = (0, 0, z)
    return obj


# ----------------------------------------------------------------------------
# prefabs — build once, instance many
# ----------------------------------------------------------------------------

def prefab_banquet_chair(frame_mat, seat_mat, name="PF_Chair"):
    """Gold-frame banquet chair: seat pad, tapered back, 4 legs, stretcher."""
    parts = []
    parts.append(bevel(box(f"{name}_seat", (0.46, 0.46, 0.07), (0, 0, 0.46), seat_mat), 0.012))
    parts.append(bevel(box(f"{name}_back", (0.44, 0.06, 0.52), (0, -0.21, 0.78), frame_mat), 0.010))
    parts.append(bevel(box(f"{name}_pad", (0.38, 0.05, 0.34), (0, -0.175, 0.76), seat_mat), 0.010))
    for i, (sx, sy) in enumerate(((-0.20, -0.20), (0.20, -0.20), (-0.20, 0.20), (0.20, 0.20))):
        parts.append(bevel(box(f"{name}_leg{i}", (0.045, 0.045, 0.46), (sx, sy, 0.23), frame_mat), 0.006))
    parts.append(bevel(box(f"{name}_str", (0.42, 0.035, 0.035), (0, 0.20, 0.18), frame_mat), 0.005))
    o = join(parts, name)
    return stash(o)


def prefab_round_table(cloth_mat, name="PF_Table", r=0.92, h=0.76):
    parts = [smooth(cyl(f"{name}_top", r, 0.05, (0, 0, h), cloth_mat, verts=48))]
    # draped skirt: slightly flared cone reads better than a straight cylinder
    bpy.ops.mesh.primitive_cone_add(radius1=r * 0.99, radius2=r * 0.86, depth=h,
                                    location=(0, 0, h / 2), vertices=48)
    skirt = bpy.context.active_object
    skirt.name = f"{name}_skirt"
    skirt.data.materials.append(cloth_mat)
    smooth(skirt)
    parts.append(skirt)
    o = join(parts, name)
    return stash(o)


def prefab_table_setting(china_mat, glass_mat, gold_mat, flower_mat, candle_mat,
                         name="PF_Setting", covers=8, r=0.92):
    """Plates, glassware, cutlery, low floral + votives. This is the detail that
    separates a layout diagram from a render a client can imagine sitting at."""
    parts = []
    for c in range(covers):
        a = 2 * math.pi * c / covers
        px, py = 0.62 * math.cos(a), 0.62 * math.sin(a)
        parts.append(smooth(cyl(f"{name}_plate{c}", 0.135, 0.016, (px, py, 0.785), china_mat, 32)))
        parts.append(smooth(cyl(f"{name}_side{c}", 0.075, 0.014, (px - 0.22 * math.sin(a),
                                                                  py + 0.22 * math.cos(a), 0.785), china_mat, 24)))
        gx, gy = 0.46 * math.cos(a + 0.10), 0.46 * math.sin(a + 0.10)
        parts.append(smooth(cyl(f"{name}_gstem{c}", 0.012, 0.10, (gx, gy, 0.83), glass_mat, 12)))
        parts.append(smooth(cyl(f"{name}_gbowl{c}", 0.042, 0.11, (gx, gy, 0.94), glass_mat, 20)))
        for k, off in enumerate((0.20, -0.20)):
            fx = px + off * math.cos(a + math.pi / 2)
            fy = py + off * math.sin(a + math.pi / 2)
            parts.append(box(f"{name}_cut{c}_{k}", (0.014, 0.16, 0.006), (fx, fy, 0.782),
                             gold_mat, rot=(0, 0, a)))
    # centrepiece: gold footed bowl + low floral dome + votives
    parts.append(smooth(cyl(f"{name}_ftr", 0.055, 0.20, (0, 0, 0.86), gold_mat, 24)))
    parts.append(smooth(cyl(f"{name}_bowl", 0.19, 0.09, (0, 0, 0.99), gold_mat, 32)))
    parts.append(smooth(sph(f"{name}_flor", 0.24, (0, 0, 1.10), flower_mat, 20, 12)))
    for k in range(5):
        a = 2 * math.pi * k / 5
        parts.append(smooth(cyl(f"{name}_vot{k}", 0.033, 0.075, (0.40 * math.cos(a),
                                                                 0.40 * math.sin(a), 0.80), candle_mat, 14)))
    o = join(parts, name)
    return stash(o)


def prefab_truss(length, mat, name="PF_Truss", side=0.38, bays=None):
    """Real lattice truss: 4 chords + zigzag webbing. Silhouette is the whole point."""
    parts = []
    hs = side / 2
    for i, (dy, dz) in enumerate(((-hs, -hs), (hs, -hs), (-hs, hs), (hs, hs))):
        parts.append(smooth(cyl(f"{name}_ch{i}", 0.030, length, (0, dy, dz), mat, 10,
                                rot=(0, math.radians(90), 0))))
    bays = bays or max(4, int(length / 0.5))
    step = length / bays
    for b in range(bays):
        x = -length / 2 + step * (b + 0.5)
        d = 1 if b % 2 == 0 else -1
        for dy in (-hs, hs):
            parts.append(smooth(cyl(f"{name}_wz{b}_{dy}", 0.014, side * 1.45, (x, dy, 0), mat, 8,
                                    rot=(math.radians(45 * d), 0, 0))))
        for dz in (-hs, hs):
            parts.append(smooth(cyl(f"{name}_wy{b}_{dz}", 0.014, side * 1.45, (x, 0, dz), mat, 8,
                                    rot=(0, 0, math.radians(45 * d)))))
    o = join(parts, name)
    return stash(o)


def prefab_moving_light(body_mat, lens_mat, name="PF_Mover"):
    parts = [
        bevel(box(f"{name}_yoke", (0.30, 0.10, 0.26), (0, 0, -0.06), body_mat), 0.010),
        bevel(box(f"{name}_head", (0.22, 0.24, 0.30), (0, 0, -0.30), body_mat), 0.014),
        smooth(cyl(f"{name}_lens", 0.095, 0.045, (0, 0, -0.46), lens_mat, 24)),
        bevel(box(f"{name}_clamp", (0.10, 0.10, 0.12), (0, 0, 0.12), body_mat), 0.006),
    ]
    o = join(parts, name)
    return stash(o)


def prefab_person(suit_mat, skin_mat, name="PF_Person", h=1.72):
    """Deliberately simple, low-contrast figure — scale reference, not a character.
    Never present these as depictions of real people."""
    parts = [
        smooth(cyl(f"{name}_legs", 0.15, h * 0.50, (0, 0, h * 0.25), suit_mat, 14)),
        smooth(cyl(f"{name}_torso", 0.19, h * 0.34, (0, 0, h * 0.67), suit_mat, 16)),
        smooth(sph(f"{name}_head", 0.105, (0, 0, h * 0.93), skin_mat, 18, 12)),
    ]
    o = join(parts, name)
    return stash(o)


def prefab_planter(pot_mat, leaf_mat, name="PF_Planter"):
    parts = [smooth(cyl(f"{name}_pot", 0.30, 0.55, (0, 0, 0.275), pot_mat, 28))]
    rng = random.Random(4)
    for i in range(9):
        a = 2 * math.pi * i / 9
        rr = 0.26 + rng.random() * 0.22
        parts.append(smooth(sph(f"{name}_l{i}", 0.20 + rng.random() * 0.10,
                                (rr * math.cos(a), rr * math.sin(a),
                                 0.72 + rng.random() * 0.34), leaf_mat, 12, 8)))
    o = join(parts, name)
    return stash(o)


# ----------------------------------------------------------------------------
# lighting / atmosphere
# ----------------------------------------------------------------------------

def gradient_world(top=(0.010, 0.013, 0.030), bottom=(0.002, 0.002, 0.004), strength=1.0):
    """Stand-in for an HDRI when none can be downloaded: vertical gradient sky."""
    scn = bpy.context.scene
    w = bpy.data.worlds.new("ZYNTH_World")
    scn.world = w
    w.use_nodes = True
    nt = w.node_tree
    nodes, links = nt.nodes, nt.links
    bg = nodes.get("Background")
    tc = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    r = nodes.new("ShaderNodeValToRGB")
    el = r.color_ramp.elements
    el[0].position, el[0].color = 0.35, (*bottom, 1)
    el[1].position, el[1].color = 0.65, (*top, 1)
    links.new(sep.outputs["Z"], r.inputs["Fac"])
    links.new(r.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    return w


def area(name, loc, size, energy, color=(1, 1, 1), rot=(0, 0, 0), shape="SQUARE",
         size_y=None, diffuse=1.0, specular=1.0):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot)
    L = bpy.context.active_object
    L.name = name
    L.data.shape = shape
    L.data.size = size
    if size_y:
        L.data.size_y = size_y
    L.data.energy = energy
    L.data.color = color
    L.data.diffuse_factor = diffuse
    L.data.specular_factor = specular
    return L


def _aim_euler(loc, target):
    import mathutils
    d = mathutils.Vector(target) - mathutils.Vector(loc)
    return d.to_track_quat("-Z", "Y").to_euler()


def spot(name, loc, target, energy, color=(1, 1, 1), angle=28.0, blend=0.35, radius=0.06):
    bpy.ops.object.light_add(type="SPOT", location=loc)
    L = bpy.context.active_object
    L.name = name
    L.data.energy = energy
    L.data.color = color
    L.data.spot_size = math.radians(angle)
    L.data.spot_blend = blend
    L.data.shadow_soft_size = radius
    L.rotation_euler = _aim_euler(loc, target)
    return L


def haze(name, dims, loc, density=0.006, color=(0.85, 0.9, 1.0), anisotropy=0.35):
    """Principled Volume box. This is what makes spotlight beams visible — the
    #1 reason a real event photo looks different from a clean 3D render."""
    o = box(name, dims, loc, None)
    m, nt, nodes, links = _newmat(f"{name}_vol")
    for n in list(nodes):
        if n.type == "BSDF_PRINCIPLED":
            nodes.remove(n)
    vol = nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (*color, 1)
    vol.inputs["Density"].default_value = density
    if "Anisotropy" in vol.inputs:
        vol.inputs["Anisotropy"].default_value = anisotropy
    out = nodes.get("Material Output")
    links.new(vol.outputs["Volume"], out.inputs["Volume"])
    o.data.materials.append(m)
    o.visible_shadow = False
    return o


# ----------------------------------------------------------------------------
# camera
# ----------------------------------------------------------------------------

def camera(name, loc, target, lens=35.0, fstop=None, focus_target=None,
           shift=(0.0, 0.0), make_active=True):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.active_object
    c.name = name
    c.data.lens = lens
    c.data.shift_x, c.data.shift_y = shift
    c.rotation_euler = _aim_euler(loc, target)
    if fstop:
        import mathutils
        c.data.dof.use_dof = True
        c.data.dof.aperture_fstop = fstop
        ft = focus_target or target
        c.data.dof.focus_distance = (mathutils.Vector(ft) - mathutils.Vector(loc)).length
    if make_active:
        bpy.context.scene.camera = c
    return c


# ----------------------------------------------------------------------------
# output
# ----------------------------------------------------------------------------

def out_dir(default_sub="zynth_3d_out"):
    d = os.environ.get("ZYNTH_3D_OUT", os.path.join(os.getcwd(), default_sub))
    os.makedirs(d, exist_ok=True)
    return d


def export(basepath, glb=True, fbx=True, blend=True):
    import addon_utils
    for a in ("io_scene_gltf2", "io_scene_fbx"):
        try:
            addon_utils.enable(a)
        except Exception:
            pass
    done = {}
    if glb:
        try:
            bpy.ops.export_scene.gltf(filepath=basepath + ".glb", export_format="GLB")
            done["glb"] = True
        except Exception as e:
            done["glb"] = f"fail: {e}"
    if fbx:
        try:
            bpy.ops.export_scene.fbx(filepath=basepath + ".fbx")
            done["fbx"] = True
        except Exception as e:
            done["fbx"] = f"fail: {e}"
    if blend:
        try:
            bpy.ops.wm.save_as_mainfile(filepath=basepath + ".blend")
            done["blend"] = True
        except Exception as e:
            done["blend"] = f"fail: {e}"
    return done


def render_shot(cam, filepath, samples=None, res=None):
    scn = bpy.context.scene
    if isinstance(cam, str):
        cam = bpy.data.objects.get(cam)
    if cam:
        scn.camera = cam
    if samples:
        scn.cycles.samples = samples
    if res:
        scn.render.resolution_x, scn.render.resolution_y = res
    scn.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    return filepath


def stats():
    return {
        "objects": len(bpy.data.objects),
        "meshes": len([o for o in bpy.data.objects if o.type == "MESH"]),
        "unique_mesh_data": len({o.data.name for o in bpy.data.objects if o.type == "MESH"}),
        "materials": len(bpy.data.materials),
        "tris": sum(len(m.loop_triangles) for m in bpy.data.meshes
                    if (m.calc_loop_triangles() or True) and m.users),
    }
