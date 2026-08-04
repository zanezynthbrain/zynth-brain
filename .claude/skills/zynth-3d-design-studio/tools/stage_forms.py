"""ZYNTH 3D Studio — Stage Form Studio.

The ballroom builder varies *palette*. This varies *architecture* — the actual shape
of the stage set. Together they give FORM x DIRECTION combinations from one codebase.

Stage sets are built in isolation on a dark studio ground (the way stage designers
present them), so these render fast and read clearly as design concepts.

FORMS
    arc       Curved LED video wall + gold-framed side panels        gala / corporate
    petal     Sculptural layered fins + circular hero portal          awards / ceremony
    chevron   Nested chevron LED frames + towers + pixel strips       concert / launch
    ribbon    Curved ribbon fins + centre screen + round podium       conference / brand

DIRECTIONS  (palette, shared with event_scene_build.py)
    aurum · obsidian · emerald · ember · lumen

Run:
    ZYNTH_FORM=petal ZYNTH_DIRECTION=aurum ZYNTH_RENDER=hero python3 stage_forms.py
    ZYNTH_FORM=chevron ZYNTH_RENDER=hero,front ZYNTH_SAMPLES=64 python3 stage_forms.py

Env: ZYNTH_FORM ZYNTH_DIRECTION ZYNTH_RENDER ZYNTH_SAMPLES ZYNTH_RES ZYNTH_3D_OUT
"""
import bpy, math, os, sys, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zynth3d as z
from event_scene_build_palettes import DIRECTIONS   # shared palette table

FORM = os.environ.get("ZYNTH_FORM", "arc").lower()
KEY = os.environ.get("ZYNTH_DIRECTION", "aurum").lower()
D = DIRECTIONS.get(KEY, DIRECTIONS["aurum"])
SAMPLES = int(os.environ.get("ZYNTH_SAMPLES", "64"))
_r = os.environ.get("ZYNTH_RES", "1600x900").lower().split("x")
RES = (int(_r[0]), int(_r[1]))
SHOTS = [s.strip() for s in os.environ.get("ZYNTH_RENDER", "").split(",") if s.strip()]

z.new_scene()
z.set_render(samples=SAMPLES, res=RES, exposure=0.30)
rng = random.Random(5)

# ---------------------------------------------------------------------------
# shared materials
# ---------------------------------------------------------------------------
GOLD = z.m_metal_brushed("Accent", D["accent"], rough=0.26)
GOLD_HI = z.m_metal_brushed("AccentPolish", D["accent"], rough=0.13)
GLOW = z.m_emissive("AccentGlow", D["accent_glow"], 2.6)
GLOW_HOT = z.m_emissive("AccentGlowHot", D["accent_glow"], 6.0)
COOL = z.m_emissive("CoolGlow", D["beam_b"], 4.0)
WARM = z.m_emissive("WarmGlow", D["beam_a"], 4.0)
BLACK = z.m_plain("Matte", (0.018, 0.018, 0.022), rough=0.72)
DECK = z.m_marble("Deck", base=D["marble"], vein=D["marble_vein"], rough=0.09)
FLOOR = z.m_plain("StudioFloor", (0.012, 0.012, 0.016), metallic=0.25, rough=0.16)
STEEL = z.m_metal_brushed("Steel", (0.36, 0.37, 0.40), rough=0.36)
PANEL = z.m_plain("Panel", (0.80, 0.81, 0.84), rough=0.30)
LENS_A = z.m_emissive("LensWarm", D["beam_a"], 22.0)
LENS_B = z.m_emissive("LensCool", D["beam_b"], 22.0)

LED_IMG = z.make_led_content("LED_Loop", 1536, 768, deep=D["led_deep"], mid=D["led_mid"],
                             gold=D["accent_glow"], swooshes=3, emblem=True, gain=0.50)
LED_ALT = z.make_led_content("LED_Alt", 1024, 1024, deep=D["led_deep"], mid=D["led_mid"],
                             gold=D["beam_b"], swooshes=4, emblem=False, gain=0.55)
LEDMAT = z.m_led_screen("LED_Main", LED_IMG, strength=1.0, px=(300, 76))
LEDSQ = z.m_led_screen("LED_Square", LED_ALT, strength=1.1, px=(150, 150))
LEDTOWER = z.m_led_screen("LED_Tower", LED_ALT, strength=1.0, px=(30, 190))

PF_TRUSS = z.prefab_truss(26.0, STEEL, "PF_TrussLong")
PF_MOVER_A = z.prefab_moving_light(BLACK, LENS_A, "PF_MoverA")
PF_MOVER_B = z.prefab_moving_light(BLACK, LENS_B, "PF_MoverB")
PF_PERSON = z.prefab_person(z.m_plain("Fig", (0.06, 0.065, 0.08), rough=0.68),
                            z.m_plain("Skin", (0.52, 0.38, 0.30), rough=0.62))

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def dot_strip(tag, p0, p1, n, mat, r=0.055):
    """Row of emissive dots between two points — the pixel-strip / bulb-trim look."""
    for i in range(n):
        t = i / max(1, n - 1)
        p = tuple(p0[k] + (p1[k] - p0[k]) * t for k in range(3))
        z.smooth(z.sph(f"Dot_{tag}_{i}", r, p, mat, 10, 6))


def riser(tag, w, d, h, loc, top_mat=DECK, side_mat=BLACK, trim=None):
    """A stage riser with a glowing edge trim — the tiered-platform language."""
    z.bevel(z.box(f"Rz_{tag}", (w, d, h), (loc[0], loc[1], loc[2] + h / 2), side_mat), 0.02)
    z.box(f"Rt_{tag}", (w, d, 0.05), (loc[0], loc[1], loc[2] + h + 0.01), top_mat)
    if trim:
        z.box(f"Rm_{tag}", (w + 0.10, d + 0.10, 0.09), (loc[0], loc[1], loc[2] + h - 0.07), trim)


def round_riser(tag, r, h, loc, top_mat=DECK, trim=None, verts=64):
    z.smooth(z.cyl(f"Cz_{tag}", r, h, (loc[0], loc[1], loc[2] + h / 2), BLACK, verts))
    z.smooth(z.cyl(f"Ct_{tag}", r * 0.995, 0.05, (loc[0], loc[1], loc[2] + h + 0.01), top_mat, verts))
    if trim:
        z.smooth(z.cyl(f"Cm_{tag}", r + 0.05, 0.10, (loc[0], loc[1], loc[2] + h - 0.08), trim, verts))


def speaker_tower(tag, x, y):
    z.bevel(z.box(f"Spk_base_{tag}", (1.5, 1.5, 0.55), (x, y, 0.275), BLACK), 0.03)
    for k in range(2):
        z.bevel(z.box(f"Spk_box_{tag}_{k}", (1.3, 1.1, 0.75), (x, y, 0.9 + k * 0.78), BLACK), 0.03)
    for k in range(4):
        z.bevel(z.box(f"Spk_arr_{tag}_{k}", (1.0, 0.85, 0.32),
                      (x, y, 3.1 + k * 0.34), BLACK), 0.02)
    for k in range(4):
        z.smooth(z.cyl(f"Spk_leg_{tag}_{k}", 0.05, 3.2,
                       (x + (0.55 if k % 2 else -0.55), y + (0.55 if k > 1 else -0.55), 1.6),
                       STEEL, 10))


def overhead_rig(y_front=-2.2, y_back=3.2, zz=9.0, n=15, span=11.0):
    z.place(PF_TRUSS, (0, y_front, zz), name="Truss_front")
    z.place(PF_TRUSS, (0, y_back, zz), name="Truss_back")
    for s, sx in ((0, -1), (1, 1)):
        for yy in (y_front, y_back):
            z.bevel(z.box(f"Leg_{s}_{yy}", (0.36, 0.36, zz), (sx * 12.6, yy, zz / 2), STEEL), 0.02)
    beams = []
    for i in range(n):
        xx = -span + i * (2 * span / (n - 1))
        z.place(PF_MOVER_A if i % 2 else PF_MOVER_B, (xx, y_front, zz - 0.32),
                name=f"Mover_F{i}")
        beams.append((xx, i % 2))
    for i in range(9):
        xx = -span * 0.8 + i * (1.6 * span * 0.8 / 8)
        z.place(PF_MOVER_B if i % 2 else PF_MOVER_A, (xx, y_back, zz - 0.32), name=f"Mover_B{i}")
    return beams


# ---------------------------------------------------------------------------
# FORM: arc — curved LED wall + framed side panels (the gala/corporate default)
# ---------------------------------------------------------------------------
def build_arc():
    riser("main", 20.0, 7.0, 1.0, (0, 3.0, 0), trim=GLOW)
    riser("thrust", 5.0, 3.4, 1.0, (0, -1.2, 0), trim=GLOW)
    for k in range(3):
        riser(f"st{k}", 5.4, 0.45, 0.33, (0, -3.1 - k * 0.45, 0.99 - (k + 1) * 0.33))
    z.curved_screen("LEDWall", 6.4, 22.0, 56.0, 6.2, 1.0, LEDMAT, nu=110, nv=22)
    z.curved_screen("LEDCase", 6.65, 22.0, 59.0, 6.6, 0.85, BLACK, nu=64, nv=6)
    cy = 6.4 - 22.0
    for i in range(13):
        phi = math.radians(-28 + i * (56 / 12))
        z.box(f"Seam_{i}", (0.04, 0.05, 6.2),
              (22.0 * math.sin(phi), cy + 22.0 * math.cos(phi) - 0.13, 4.1), BLACK, rot=(0, 0, -phi))
    for s, sx in ((0, -1), (1, 1)):
        z.bevel(z.box(f"Frame_{s}", (3.0, 0.45, 6.6), (sx * 11.6, 5.6, 4.3), GOLD), 0.04)
        z.box(f"FPanel_{s}", (2.6, 0.20, 6.1), (sx * 11.6, 5.42, 4.3), LEDTOWER)
        z.smooth(z.torus(f"Emb_{s}", 0.62, 0.07, (sx * 11.6, 5.26, 4.9), GOLD_HI,
                         rot=(math.radians(90), 0, 0)))
        speaker_tower(f"{s}", sx * 13.4, 1.0)
    z.bevel(z.box("Lectern", (1.0, 0.7, 1.2), (-6.0, 1.2, 1.6), PANEL), 0.03)
    z.box("Lectern_f", (0.8, 0.06, 0.62), (-6.0, 0.86, 1.78), COOL)
    return overhead_rig()


# ---------------------------------------------------------------------------
# FORM: petal — sculptural layered fins + circular hero portal (awards/ceremony)
# ---------------------------------------------------------------------------
def build_petal():
    # tiered curved platforms with bulb trim
    round_riser("p0", 8.2, 0.55, (0, 2.0, 0), trim=GLOW)
    round_riser("p1", 6.2, 0.50, (0, 2.6, 0.55), trim=GLOW)
    round_riser("p2", 4.0, 0.45, (0, 3.2, 1.05), trim=GLOW)
    for k, (rr, zz) in enumerate(((8.2, 0.50), (6.2, 1.00), (4.0, 1.45))):
        for i in range(26):
            a = math.radians(-96 + i * (192 / 25))
            z.smooth(z.sph(f"Bulb_{k}_{i}", 0.085,
                           (rr * math.sin(a), 2.0 + 0.6 * k + rr * math.cos(a) * 0.55, zz),
                           GLOW_HOT, 10, 6))
    # sculptural petal fins — layered curved blades fanning out behind the portal
    for i in range(9):
        t = (i - 4) / 4.0
        lean = math.radians(t * 34)
        h = 8.6 - abs(t) * 2.2
        rad = 9.0 + abs(t) * 4.0
        span = 26 - abs(t) * 7
        apex = 7.6 - abs(t) * 1.1
        fin = z.curved_screen(f"Petal_{i}", apex, rad, span, h, 0.4,
                              LEDSQ if i % 2 == 0 else COOL, nu=26, nv=10)
        fin.location = (t * 4.4, -abs(t) * 0.7, 0)
        fin.rotation_euler = (0, lean, math.radians(-t * 16))
        z.smooth(fin)
    # hero circular portal
    z.smooth(z.torus("Portal_ring", 2.55, 0.30, (0, 6.6, 4.4), GOLD, rot=(math.radians(90), 0, 0)))
    z.smooth(z.torus("Portal_in", 2.05, 0.10, (0, 6.45, 4.4), GLOW, rot=(math.radians(90), 0, 0)))
    z.smooth(z.cyl("Portal_face", 2.05, 0.16, (0, 6.75, 4.4), BLACK, 48, rot=(math.radians(90), 0, 0)))
    for i in range(16):
        a = 2 * math.pi * i / 16
        z.smooth(z.sph(f"Portal_dot_{i}", 0.115,
                       (2.55 * math.cos(a), 6.42, 4.4 + 2.55 * math.sin(a)), GLOW_HOT, 10, 6))
    # hero object on a plinth inside the portal (abstract award form)
    z.smooth(z.cyl("Plinth", 0.55, 1.0, (0, 6.7, 2.3), GOLD_HI, 32))
    z.smooth(z.cyl("Plinth_top", 0.70, 0.12, (0, 6.7, 2.86), GOLD, 32))
    z.smooth(z.sph("Award_b", 0.42, (0, 6.7, 3.35), GOLD_HI, 20, 14))
    aw = z.smooth(z.sph("Award_t", 0.62, (0, 6.7, 4.25), GOLD_HI, 20, 14))
    aw.scale = (0.55, 0.55, 1.5)
    z.bevel(z.box("Podium", (1.1, 0.75, 1.15), (-5.4, 3.4, 2.13), BLACK), 0.03)
    for s, sx in ((0, -1), (1, 1)):
        speaker_tower(f"{s}", sx * 13.0, 0.5)
    return overhead_rig(y_front=-1.6, y_back=4.0, zz=9.6, n=15, span=10.5)


# ---------------------------------------------------------------------------
# FORM: chevron — nested chevron LED frames + towers + pixel strips (concert/launch)
# ---------------------------------------------------------------------------
def build_chevron():
    riser("main", 18.0, 6.0, 1.2, (0, 2.6, 0), trim=GLOW)
    riser("thrust", 6.0, 3.0, 1.2, (0, -1.4, 0), trim=GLOW)
    # nested chevrons — each a pair of angled LED blades meeting at the apex
    for i in range(5):
        k = i / 4.0
        w = 11.5 - i * 1.9          # blade length
        lift = 1.2 + i * 1.15       # apex height
        depth = 6.4 - i * 0.95
        ang = math.radians(26 + i * 4)
        for s, sx in ((0, -1), (1, 1)):
            blade = z.box(f"Chev_{i}_{s}", (w, 0.30, 1.5 - i * 0.14),
                          (sx * (w / 2) * math.cos(ang), depth,
                           lift + (w / 2) * math.sin(ang) * 0.55),
                          LEDSQ if i % 2 == 0 else COOL,
                          rot=(0, sx * -ang, 0))
            z.bevel(blade, 0.02)
            # pixel dot strip along the leading edge
            dot_strip(f"c{i}{s}", (0, depth - 0.22, lift + 0.1),
                      (sx * w * math.cos(ang), depth - 0.22,
                       lift + w * math.sin(ang) * 0.55), 14 - i * 2, GLOW_HOT, r=0.055)
    # central apex screen
    z.box("Apex_screen", (5.6, 0.25, 4.2), (0, 7.2, 4.4), LEDMAT)
    # vertical LED towers flanking
    for s, sx in ((0, -1), (1, 1)):
        for k in range(2):
            z.box(f"Tower_{s}_{k}", (0.95, 0.28, 8.0), (sx * (9.6 + k * 1.35), 6.2, 4.4), LEDTOWER)
            dot_strip(f"t{s}{k}", (sx * (9.6 + k * 1.35), 5.98, 0.6),
                      (sx * (9.6 + k * 1.35), 5.98, 8.3), 16, GLOW_HOT, r=0.05)
        speaker_tower(f"{s}", sx * 13.6, 0.8)
    # floor pixel strips fanning downstage
    for i in range(5):
        xx = -6.0 + i * 3.0
        dot_strip(f"f{i}", (xx, -1.0, 1.27), (xx * 1.7, -4.6, 0.06), 12, COOL, r=0.05)
    return overhead_rig(y_front=-2.6, y_back=4.4, zz=10.0, n=17, span=12.0)


# ---------------------------------------------------------------------------
# FORM: ribbon — curved ribbon fins + centre screen + round podium (conference/brand)
# ---------------------------------------------------------------------------
def build_ribbon():
    # circular tiered podium with strong glowing edges
    round_riser("r0", 7.4, 0.42, (0, 0.4, 0), trim=GLOW_HOT)
    round_riser("r1", 5.9, 0.40, (0, 0.4, 0.42), trim=GLOW_HOT)
    round_riser("r2", 4.4, 0.38, (0, 0.4, 0.82), trim=GLOW_HOT)
    # wings either side
    for s, sx in ((0, -1), (1, 1)):
        round_riser(f"w{s}", 2.6, 0.80, (sx * 6.6, 2.2, 0), trim=GLOW_HOT, verts=48)
    # rear straight risers up to the screen
    for k in range(3):
        riser(f"b{k}", 11.0 - k * 1.2, 0.55, 1.2 + k * 0.42, (0, 5.0 + k * 0.55, 0), trim=GLOW_HOT)
    # centre rounded LED screen in a white bezel
    z.bevel(z.box("Screen_bezel", (11.4, 0.42, 5.6), (0, 7.6, 5.0), PANEL), 0.16)
    z.box("Screen", (10.6, 0.20, 4.9), (0, 7.36, 5.0), LEDMAT)
    # side LED slabs
    for s, sx in ((0, -1), (1, 1)):
        z.bevel(z.box(f"SideSlab_{s}", (2.5, 0.34, 5.2), (sx * 7.3, 7.6, 4.8), PANEL), 0.14)
        z.box(f"SideLED_{s}", (2.1, 0.18, 4.7), (sx * 7.3, 7.40, 4.8), LEDTOWER)
        # curved white ribbon fins
        for k in range(5):
            fin = z.curved_screen(f"Ribbon_{s}_{k}", 8.4 - k * 0.30, 9.0, 15.0,
                                  5.4 - k * 0.28, 1.1 + k * 0.10, PANEL, nu=20, nv=8)
            fin.location = (sx * (10.4 + k * 0.62), 0, 0)
            fin.rotation_euler = (0, math.radians(sx * (7 + k * 2.5)), 0)
            z.smooth(fin)
        # brand disc on a stand
        z.smooth(z.cyl(f"Disc_{s}", 1.20, 0.22, (sx * 12.4, 6.0, 4.3), GOLD,
                       32, rot=(math.radians(90), 0, 0)))
        z.smooth(z.cyl(f"DiscIn_{s}", 0.92, 0.10, (sx * 12.4, 5.86, 4.3), GLOW,
                       32, rot=(math.radians(90), 0, 0)))
        z.bevel(z.box(f"Sign_{s}", (3.4, 0.22, 1.0), (sx * 12.4, 5.4, 2.5), PANEL), 0.05)
        z.box(f"SignGlow_{s}", (3.0, 0.10, 0.55), (sx * 12.4, 5.24, 2.5), COOL)
        speaker_tower(f"{s}", sx * 15.4, 2.0)
    z.bevel(z.box("Lectern", (0.95, 0.68, 1.20), (0, 3.4, 1.80), PANEL), 0.04)
    z.box("Lectern_f", (0.78, 0.06, 0.60), (0, 3.07, 1.95), COOL)
    return overhead_rig(y_front=-2.0, y_back=5.6, zz=9.4, n=15, span=11.5)


FORMS = {"arc": build_arc, "petal": build_petal,
         "chevron": build_chevron, "ribbon": build_ribbon}

# ---------------------------------------------------------------------------
# studio environment
# ---------------------------------------------------------------------------
z.box("Ground", (90, 90, 0.10), (0, 0, -0.05), FLOOR)
beams = FORMS.get(FORM, build_arc)()

# a few figures for scale, downstage
for i, (px, py) in enumerate([(-4.2, -5.6), (3.6, -6.4), (7.4, -4.8), (-8.2, -4.2)]):
    z.place(PF_PERSON, (px, py, 0), rot_z=rng.random() * 6.28, name=f"Figure_{i}")

z.gradient_world(top=(0.006, 0.008, 0.018), bottom=(0.001, 0.001, 0.003), strength=1.0)
z.area("Key", (0, -7.0, 8.0), 8.0, 900, D["beam_a"])
z.area("Fill", (0, 6.0, 7.0), 10.0, 260, D["beam_b"])
z.area("Rim_L", (-13.0, 3.0, 6.0), 5.0, 300, D["accent_glow"])
z.area("Rim_R", (13.0, 3.0, 6.0), 5.0, 300, D["accent_glow"])
for i, (xx, warm) in enumerate(beams):
    if i % 2:
        continue
    z.spot(f"Beam_{i}", (xx, -2.2, 8.6), (xx * 0.35, 4.0, 1.2), 16000,
           D["beam_a"] if warm else D["beam_b"], angle=7.0, blend=0.14, radius=0.015)
for i, xx in enumerate((-8.5, -3.0, 3.0, 8.5)):
    z.spot(f"Sweep_{i}", (xx, -2.2, 8.6), (xx * 2.6, -14.0, 2.0), 20000,
           D["beam_b"] if i % 2 else D["beam_a"], angle=6.0, blend=0.12, radius=0.015)
z.haze("Haze", (40, 34, 12), (0, 0, 6.0), density=0.0155, color=(0.88, 0.92, 1.00))

CAMS = {
    "hero": z.camera("CAM_HERO", (-13.5, -16.5, 4.6), (0.5, 4.0, 3.6),
                     lens=34, fstop=5.0, focus_target=(0, 4.0, 3.4), make_active=True),
    "front": z.camera("CAM_FRONT", (0, -22.0, 5.2), (0, 4.0, 3.8), lens=38, make_active=False),
    "low": z.camera("CAM_LOW", (-7.0, -10.5, 1.5), (0, 4.5, 4.4), lens=28,
                    fstop=3.2, make_active=False),
}
bpy.context.scene.camera = CAMS["hero"]

OUT = z.out_dir()
BASE = os.path.join(OUT, f"STAGE_{FORM}_{KEY}")
print("STATS", z.stats(), flush=True)
print("EXPORT", z.export(BASE), flush=True)
for shot in SHOTS:
    cam = CAMS.get(shot)
    if not cam:
        print("no such camera:", shot, flush=True)
        continue
    p = os.path.join(OUT, f"STAGE_{FORM}_{KEY}_{shot}.png")
    print("RENDERING", FORM, KEY, shot, flush=True)
    z.render_shot(cam, p)
    print("RENDERED", p, flush=True)
print("DONE", FORM, KEY, flush=True)
