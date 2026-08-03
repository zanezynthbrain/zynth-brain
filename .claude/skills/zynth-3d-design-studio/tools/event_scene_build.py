"""ZYNTH 3D Studio — detailed corporate-event ballroom builder (AURUM v3).

Built on zynth3d.py. Every detail lever is applied: beveled edges, real instanced
banquet chairs and full table settings, lattice truss with real moving heads,
procedural carpet/wood/marble/brushed-gold, a generated LED content loop with a
pixel grid, volumetric haze so the beams read, AgX tonemapping, DOF cameras.

DESIGN DIRECTIONS — the variety system. Same architecture, different art direction:
    aurum      gold + navy, warm wood, black-tie gala          (ZYNTH house)
    obsidian   monochrome + white light, minimal, tech keynote
    emerald    emerald + brass, botanical, luxury hospitality
    ember      copper + oxblood, moody, awards night
    lumen      white + ice blue, clean, pharma / medical congress

Run:
    python3 event_scene_build.py                    # aurum, build + export only
    ZYNTH_DIRECTION=obsidian python3 event_scene_build.py
    ZYNTH_RENDER=iso,stage,plan,booth python3 event_scene_build.py
    ZYNTH_SAMPLES=96 ZYNTH_RES=2048x1152 python3 event_scene_build.py

Env:
    ZYNTH_3D_OUT    output dir (default ./zynth_3d_out)
    ZYNTH_DIRECTION design direction key (default aurum)
    ZYNTH_RENDER    comma list of cameras to render (default none — build only)
    ZYNTH_SAMPLES   cycles samples (default 64)
    ZYNTH_RES       WxH (default 1600x900)

Venue basis: Novotel Yangon ballroom proportions — 32 m x 42 m x 10 m clear.
Confirm real dimensions with the venue before quoting build costs.
"""
import bpy, math, os, sys, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zynth3d as z

# ---------------------------------------------------------------------------
# design directions
# ---------------------------------------------------------------------------
DIRECTIONS = {
    "aurum": dict(
        carpet=(0.030, 0.045, 0.130), wall_dark=(0.115, 0.070, 0.032),
        wall_light=(0.290, 0.185, 0.090), accent=(0.83, 0.65, 0.22),
        accent_glow=(1.00, 0.76, 0.30), led_deep=(0.02, 0.09, 0.34),
        led_mid=(0.06, 0.26, 0.72), beam_a=(1.00, 0.78, 0.38),
        beam_b=(0.35, 0.55, 1.00), cloth=(0.93, 0.91, 0.86),
        marble=(0.045, 0.050, 0.075), marble_vein=(0.50, 0.47, 0.42),
    ),
    "obsidian": dict(
        carpet=(0.022, 0.022, 0.026), wall_dark=(0.030, 0.030, 0.034),
        wall_light=(0.105, 0.105, 0.115), accent=(0.78, 0.79, 0.82),
        accent_glow=(0.92, 0.95, 1.00), led_deep=(0.02, 0.02, 0.03),
        led_mid=(0.30, 0.34, 0.40), beam_a=(0.95, 0.97, 1.00),
        beam_b=(0.72, 0.78, 0.92), cloth=(0.10, 0.10, 0.11),
        marble=(0.030, 0.030, 0.034), marble_vein=(0.55, 0.56, 0.58),
    ),
    "emerald": dict(
        carpet=(0.020, 0.055, 0.040), wall_dark=(0.055, 0.075, 0.055),
        wall_light=(0.150, 0.190, 0.150), accent=(0.72, 0.55, 0.24),
        accent_glow=(0.95, 0.74, 0.34), led_deep=(0.01, 0.10, 0.07),
        led_mid=(0.06, 0.34, 0.24), beam_a=(0.95, 0.80, 0.42),
        beam_b=(0.35, 0.90, 0.65), cloth=(0.94, 0.93, 0.88),
        marble=(0.040, 0.055, 0.048), marble_vein=(0.52, 0.55, 0.48),
    ),
    "ember": dict(
        carpet=(0.075, 0.020, 0.022), wall_dark=(0.080, 0.045, 0.030),
        wall_light=(0.190, 0.115, 0.070), accent=(0.72, 0.42, 0.20),
        accent_glow=(1.00, 0.55, 0.22), led_deep=(0.14, 0.03, 0.02),
        led_mid=(0.52, 0.16, 0.06), beam_a=(1.00, 0.58, 0.26),
        beam_b=(0.90, 0.30, 0.20), cloth=(0.90, 0.86, 0.80),
        marble=(0.060, 0.038, 0.032), marble_vein=(0.48, 0.40, 0.34),
    ),
    "lumen": dict(
        carpet=(0.140, 0.155, 0.180), wall_dark=(0.300, 0.320, 0.350),
        wall_light=(0.640, 0.665, 0.700), accent=(0.62, 0.76, 0.92),
        accent_glow=(0.78, 0.90, 1.00), led_deep=(0.05, 0.14, 0.26),
        led_mid=(0.30, 0.62, 0.90), beam_a=(0.92, 0.96, 1.00),
        beam_b=(0.55, 0.78, 1.00), cloth=(0.96, 0.96, 0.97),
        marble=(0.500, 0.520, 0.545), marble_vein=(0.82, 0.84, 0.86),
    ),
}
KEY = os.environ.get("ZYNTH_DIRECTION", "aurum").lower()
D = DIRECTIONS.get(KEY, DIRECTIONS["aurum"])

SAMPLES = int(os.environ.get("ZYNTH_SAMPLES", "64"))
_res = os.environ.get("ZYNTH_RES", "1600x900").lower().split("x")
RES = (int(_res[0]), int(_res[1]))
SHOTS = [s.strip() for s in os.environ.get("ZYNTH_RENDER", "").split(",") if s.strip()]

# venue envelope (metres)
W, L, H = 32.0, 42.0, 10.0
STAGE_Y, STAGE_D, STAGE_W, STAGE_H = 17.5, 7.0, 19.0, 1.0

# ---------------------------------------------------------------------------
z.new_scene()
z.set_render(samples=SAMPLES, res=RES, exposure=0.35)
rng = random.Random(9)

# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------
CARPET = z.m_carpet("Carpet", D["carpet"])
WOOD = z.m_wood("WallWood", dark=D["wall_dark"], light=D["wall_light"])
GOLD = z.m_metal_brushed("Accent", D["accent"], rough=0.26)
GOLD_HI = z.m_metal_brushed("AccentPolish", D["accent"], rough=0.14)
GLOW = z.m_emissive("AccentGlow", D["accent_glow"], 1.8)
MARBLE = z.m_marble("Marble", base=D["marble"], vein=D["marble_vein"], rough=0.07)
CLOTH = z.m_fabric("TableCloth", D["cloth"], sheen=0.5, rough=0.80)
DRAPE = z.m_fabric("Drape", [c * 0.35 for c in D["wall_dark"]], scale=90.0, sheen=0.7)
CHINA = z.m_plain("China", (0.94, 0.94, 0.95), rough=0.18)
GLASSM = z.m_glass("Glassware")
BLACK = z.m_plain("Matte", (0.020, 0.020, 0.024), rough=0.70)
STEEL = z.m_metal_brushed("Steel", (0.34, 0.35, 0.38), rough=0.38)
PANEL = z.m_plain("PanelWhite", (0.78, 0.79, 0.82), rough=0.30)
LEAF = z.m_plain("Leaf", (0.045, 0.150, 0.060), rough=0.62)
FLORAL = z.m_plain("Floral", (0.90, 0.87, 0.80), rough=0.55, sheen=0.4)
CANDLE = z.m_emissive("Candle", (1.00, 0.62, 0.26), 9.0)
SOFA = z.m_fabric("Sofa", (0.42, 0.40, 0.37), scale=120.0, sheen=0.35)
SKIN = z.m_plain("Fig_skin", (0.52, 0.38, 0.30), rough=0.62)
SUIT = z.m_plain("Fig_suit", (0.055, 0.060, 0.075), rough=0.68)
LENS_A = z.m_emissive("LensWarm", D["beam_a"], 24.0)
LENS_B = z.m_emissive("LensCool", D["beam_b"], 24.0)

LED_IMG = z.make_led_content("LED_Loop", 1536, 768,
                             deep=D["led_deep"], mid=D["led_mid"],
                             gold=D["accent_glow"], swooshes=3, emblem=True)
LEDMAT = z.m_led_screen("LED_Wall", LED_IMG, strength=1.9, px=(300, 76), pixel_depth=0.45)
LED_SIDE = z.m_led_screen("LED_Side", LED_IMG, strength=1.4, px=(40, 92), pixel_depth=0.40)
SCREEN = z.m_emissive("BoothScreen", D["led_mid"], 1.1)

# ---------------------------------------------------------------------------
# prefabs (built once, instanced everywhere)
# ---------------------------------------------------------------------------
PF_CHAIR = z.prefab_banquet_chair(GOLD, CLOTH)
PF_TABLE = z.prefab_round_table(CLOTH)
PF_SET = z.prefab_table_setting(CHINA, GLASSM, GOLD_HI, FLORAL, CANDLE)
PF_MOVER_A = z.prefab_moving_light(BLACK, LENS_A, "PF_MoverA")
PF_MOVER_B = z.prefab_moving_light(BLACK, LENS_B, "PF_MoverB")
PF_PERSON = z.prefab_person(SUIT, SKIN)
PF_PLANT = z.prefab_planter(PANEL, LEAF)
PF_TRUSS_MAIN = z.prefab_truss(STAGE_W + 2.0, STEEL, "PF_TrussMain")
PF_TRUSS_SIDE = z.prefab_truss(STAGE_D + 3.0, STEEL, "PF_TrussSide")

# ---------------------------------------------------------------------------
# room shell
# ---------------------------------------------------------------------------
z.box("Floor", (W, L, 0.06), (0, 0, -0.03), CARPET)
# polished apron (reflections are what sell an event render)
z.box("Apron", (W - 3.0, 4.2, 0.02), (0, 12.2, 0.012), MARBLE)
z.box("Ceiling", (W, L, 0.20), (0, 0, H), z.m_plain("Ceiling", (0.055, 0.055, 0.062), rough=0.85))
for nm, dims, loc in (("WallBack", (W, 0.35, H), (0, L / 2 - 0.2, H / 2)),
                      ("WallFront", (W, 0.35, H), (0, -L / 2 + 0.2, H / 2)),
                      ("WallL", (0.35, L, H), (-W / 2 + 0.2, 0, H / 2)),
                      ("WallR", (0.35, L, H), (W / 2 - 0.2, 0, H / 2))):
    z.bevel(z.box(nm, dims, loc, WOOD), 0.02)
# fluted wood pilasters + accent cove
for i, yy in enumerate(range(-19, 20, 4)):
    for sx in (-1, 1):
        z.bevel(z.box(f"Pil_{sx}_{i}", (0.30, 1.30, H - 1.6),
                      (sx * (W / 2 - 0.45), yy, (H - 1.6) / 2), WOOD), 0.02)
z.box("Cove_B", (W - 1.2, 0.12, 0.22), (0, L / 2 - 0.45, H - 1.35), GLOW)
for sx in (-1, 1):
    z.box(f"Cove_{sx}", (0.12, L - 1.2, 0.22), (sx * (W / 2 - 0.45), 0, H - 1.35), GLOW)

# ---------------------------------------------------------------------------
# stage
# ---------------------------------------------------------------------------
z.bevel(z.box("Stage_riser", (STAGE_W, STAGE_D, STAGE_H), (0, STAGE_Y, STAGE_H / 2), BLACK), 0.03)
z.box("Stage_deck", (STAGE_W, STAGE_D, 0.04), (0, STAGE_Y, STAGE_H + 0.01), MARBLE)
z.box("Stage_edge", (STAGE_W + 0.12, STAGE_D + 0.12, 0.06), (0, STAGE_Y, STAGE_H - 0.06), GLOW)
# thrust
z.bevel(z.box("Thrust", (4.6, 3.2, STAGE_H), (0, STAGE_Y - STAGE_D / 2 - 1.4, STAGE_H / 2), BLACK), 0.03)
z.box("Thrust_deck", (4.6, 3.2, 0.04), (0, STAGE_Y - STAGE_D / 2 - 1.4, STAGE_H + 0.01), MARBLE)
for k in range(3):
    z.bevel(z.box(f"Step_{k}", (5.0, 0.42, 0.34),
                  (0, STAGE_Y - STAGE_D / 2 - 3.1 + k * 0.42, 0.17 + (2 - k) * 0.33), MARBLE), 0.012)

# curved LED video wall — arc of panels, concave to the audience
ARC_APEX, ARC_R, ARC_SPAN = 20.30, 22.0, 56.0     # apex y, curve radius, arc span
z.curved_screen("LED_Wall_surface", ARC_APEX, ARC_R, ARC_SPAN, 6.20, 0.95, LEDMAT, nu=110, nv=22)
z.curved_screen("LED_Wall_case", ARC_APEX + 0.22, ARC_R, ARC_SPAN + 3.0, 6.60, 0.78, BLACK,
                nu=64, nv=6)
# panel seam battens — keeps the modular-LED read without breaking the UV map
_ccy = ARC_APEX - ARC_R
for i in range(13):
    phi = math.radians(-ARC_SPAN / 2 + i * (ARC_SPAN / 12))
    z.box(f"LEDseam_{i:02d}", (0.04, 0.05, 6.20),
          (ARC_R * math.sin(phi), _ccy + ARC_R * math.cos(phi) - 0.13, 4.05),
          BLACK, rot=(0, 0, -phi))
# gold-framed side panels with emblem
for s, sx in ((0, -1), (1, 1)):
    px = sx * 11.4
    z.bevel(z.box(f"SideFrame_{s}", (2.95, 0.42, 6.5), (px, STAGE_Y + 3.05, 4.0), GOLD), 0.03)
    z.box(f"SidePanel_{s}", (2.55, 0.20, 6.0), (px, STAGE_Y + 2.90, 4.0), LED_SIDE)
    z.smooth(z.torus(f"Emblem_{s}", 0.62, 0.07, (px, STAGE_Y + 2.74, 4.6), GOLD_HI,
                     rot=(math.radians(90), 0, 0)))
# stage drape returns
for s, sx in ((0, -1), (1, 1)):
    z.box(f"Drape_{s}", (0.30, 5.0, 7.6), (sx * 13.6, STAGE_Y + 1.2, 3.8), DRAPE)
# line-array speaker hangs
for s, sx in ((0, -1), (1, 1)):
    for k in range(4):
        z.bevel(z.box(f"Array_{s}_{k}", (0.62, 0.85, 0.34),
                      (sx * 10.6, STAGE_Y - 1.4, 7.2 - k * 0.36), BLACK), 0.02)
# lectern
z.bevel(z.box("Lectern", (1.00, 0.68, 1.20), (-6.2, STAGE_Y - 1.6, STAGE_H + 0.60), PANEL), 0.03)
z.box("Lectern_face", (0.80, 0.06, 0.62), (-6.2, STAGE_Y - 1.95, STAGE_H + 0.78), SCREEN)
z.smooth(z.cyl("Mic", 0.012, 0.42, (-6.2, STAGE_Y - 1.75, STAGE_H + 1.42), BLACK, 8,
               rot=(math.radians(22), 0, 0)))
# planted hedge line at stage front
for j, xx in enumerate(range(-9, 10, 2)):
    z.place(PF_PLANT, (xx, STAGE_Y - STAGE_D / 2 - 0.55, 0), rot_z=rng.random() * 3.14,
            scale=(0.85, 0.85, 0.70), name=f"Hedge_{j}")

# ---------------------------------------------------------------------------
# rig — lattice truss + moving heads
# ---------------------------------------------------------------------------
TRUSS_Z = 8.1
z.place(PF_TRUSS_MAIN, (0, STAGE_Y - STAGE_D / 2 - 0.6, TRUSS_Z), name="Truss_front")
z.place(PF_TRUSS_MAIN, (0, STAGE_Y + STAGE_D / 2 + 0.4, TRUSS_Z), name="Truss_back")
for s, sx in ((0, -1), (1, 1)):
    z.place(PF_TRUSS_SIDE, (sx * (STAGE_W / 2 + 0.9), STAGE_Y, TRUSS_Z),
            rot=(0, 0, math.radians(90)), name=f"Truss_side_{s}")
    for k in range(2):
        z.bevel(z.box(f"TrussLeg_{s}_{k}", (0.34, 0.34, TRUSS_Z),
                      (sx * (STAGE_W / 2 + 0.9), STAGE_Y + (-3.4 if k else 3.4),
                       TRUSS_Z / 2), STEEL), 0.02)
MOVERS = []
for i in range(13):
    xx = -9.6 + i * 1.6
    z.place(PF_MOVER_A if i % 2 else PF_MOVER_B,
            (xx, STAGE_Y - STAGE_D / 2 - 0.6, TRUSS_Z - 0.30), name=f"Mover_F{i}")
    MOVERS.append((xx, i % 2))
for i in range(9):
    xx = -8.0 + i * 2.0
    z.place(PF_MOVER_A if i % 2 == 0 else PF_MOVER_B,
            (xx, STAGE_Y + STAGE_D / 2 + 0.4, TRUSS_Z - 0.30), name=f"Mover_B{i}")

# ---------------------------------------------------------------------------
# runway + seating
# ---------------------------------------------------------------------------
z.box("Runway", (3.0, 13.0, 0.10), (0, 6.6, 0.05), MARBLE)
z.box("Runway_edge", (3.16, 13.0, 0.03), (0, 6.6, 0.085), GLOW)

TABLE_X = (3.4, 6.6, 9.8)
TABLE_Y = (1.4, 4.9, 8.4, 11.6)
n_t = 0
for sx in (-1, 1):
    for cx in TABLE_X:
        for ry in TABLE_Y:
            x, y = sx * cx, ry
            z.place(PF_TABLE, (x, y, 0), name=f"Table_{n_t}")
            z.place(PF_SET, (x, y, 0), rot_z=rng.random() * 0.8, name=f"Setting_{n_t}")
            for c in range(8):
                a = 2 * math.pi * c / 8 + rng.random() * 0.10
                z.place(PF_CHAIR, (x + 1.42 * math.cos(a), y + 1.42 * math.sin(a), 0),
                        rot_z=a + math.pi / 2, name=f"Chair_{n_t}_{c}")
            n_t += 1

# ---------------------------------------------------------------------------
# exhibition booths — illuminated portals down both walls
# ---------------------------------------------------------------------------
def booth(tag, x, y, inward):
    z.bevel(z.box(f"Bth_pL_{tag}", (0.32, 0.34, 4.10), (x, y - 1.85, 2.05), PANEL), 0.02)
    z.bevel(z.box(f"Bth_pR_{tag}", (0.32, 0.34, 4.10), (x, y + 1.85, 2.05), PANEL), 0.02)
    z.box(f"Bth_head_{tag}", (0.34, 4.04, 0.40), (x, y, 4.05), GOLD)
    z.box(f"Bth_hglow_{tag}", (0.20, 3.90, 0.10), (x + 0.16 * inward, y, 3.86), GLOW)
    z.box(f"Bth_back_{tag}", (0.14, 3.40, 3.60), (x + 0.22 * inward, y, 1.80), PANEL)
    z.box(f"Bth_screen_{tag}", (0.07, 1.80, 1.60), (x + 0.42 * inward, y + 0.55, 2.30), SCREEN)
    z.bevel(z.box(f"Bth_ctr_{tag}", (1.10, 2.60, 1.05),
                  (x + 1.25 * inward, y - 0.30, 0.525), PANEL), 0.02)
    z.box(f"Bth_ctrglow_{tag}", (1.06, 2.50, 0.03), (x + 1.25 * inward, y - 0.30, 1.06), GLOW)
    z.bevel(z.box(f"Bth_pl_{tag}", (0.55, 0.55, 1.15),
                  (x + 1.10 * inward, y + 1.30, 0.575), GOLD), 0.02)
    z.smooth(z.cyl(f"Bth_obj_{tag}", 0.20, 0.34, (x + 1.10 * inward, y + 1.30, 1.32), GOLD_HI, 24))
    z.box(f"Bth_floor_{tag}", (2.60, 4.00, 0.04), (x + 1.0 * inward, y, 0.02), MARBLE)

for i, yy in enumerate((-6.6, -2.2, 2.2, 6.6, 11.0)):
    booth(f"L{i}", -(W / 2 - 1.4), yy, +1)
    booth(f"R{i}", (W / 2 - 1.4), yy, -1)

# ---------------------------------------------------------------------------
# entrance: gold WELCOME arch + runner
# ---------------------------------------------------------------------------
AY = -13.0
for s, sx in ((0, -1), (1, 1)):
    z.bevel(z.box(f"Arch_post_{s}", (0.90, 1.00, 3.70), (sx * 3.1, AY, 1.85), GOLD), 0.04)
    z.smooth(z.torus(f"Arch_med_{s}", 0.42, 0.06, (sx * 2.55, AY - 0.52, 1.70), GOLD_HI,
                     rot=(math.radians(90), 0, 0)))
z.bevel(z.box("Arch_lintel", (7.9, 1.00, 1.00), (0, AY, 4.05), GOLD), 0.04)
z.box("Arch_inner", (6.4, 0.44, 0.42), (0, AY, 3.66), GLOW)
bpy.ops.object.text_add(location=(0, AY - 0.56, 3.98))
_t = bpy.context.active_object
_t.name = "WelcomeText"
_t.data.body = "WELCOME"
_t.data.size = 0.60
_t.data.extrude = 0.05
_t.data.bevel_depth = 0.006
_t.data.align_x = "CENTER"
_t.rotation_euler = (math.radians(90), 0, 0)
_t.data.materials.append(GLOW)
bpy.ops.object.convert(target="MESH")
z.box("Runner", (3.0, 8.0, 0.02), (0, -8.6, 0.012), MARBLE)

# ---------------------------------------------------------------------------
# left zone — photo booth + registration + cocktail
# ---------------------------------------------------------------------------
RING = z.m_emissive("RingLight", (1.0, 0.94, 0.86), 7.0)
z.box("Photo_drape", (4.6, 0.34, 3.40), (-11.6, -17.0, 1.70), DRAPE)
for s, sx in ((0, -1), (1, 1)):
    z.bevel(z.box(f"Photo_post_{s}", (0.34, 0.34, 3.10), (-11.6 + sx * 1.85, -16.2, 1.55), GOLD), 0.02)
    z.smooth(z.cyl(f"Photo_ring_{s}", 0.46, 0.09, (-11.6 + sx * 2.60, -15.4, 2.30), RING, 28,
                   rot=(math.radians(90), 0, 0)))
z.bevel(z.box("Photo_head", (4.20, 0.34, 0.40), (-11.6, -16.2, 3.28), GOLD), 0.02)
z.box("Photo_bench", (2.20, 0.60, 0.46), (-11.6, -15.6, 0.23), GOLD)
# registration desk (segmented curve)
for k in range(5):
    a = math.radians(-32 + k * 16)
    z.bevel(z.box(f"Reg_{k}", (1.30, 0.80, 1.10),
                  (-9.2 + k * 1.32, -11.4 + 0.34 * math.sin(a), 0.55),
                  PANEL, rot=(0, 0, a * 0.35)), 0.02)
z.box("Reg_glow", (6.40, 0.10, 0.06), (-6.6, -11.05, 1.08), GLOW)
z.bevel(z.box("Reg_kiosk", (0.90, 0.14, 1.50), (-10.8, -11.4, 1.60), SCREEN), 0.02)
for i, (px, py) in enumerate([(-6.4, -17.2), (-4.6, -15.6), (-6.8, -14.4), (-4.2, -17.8)]):
    z.smooth(z.cyl(f"Poseur_st_{i}", 0.10, 1.05, (px, py, 0.525), STEEL, 16))
    z.smooth(z.cyl(f"Poseur_bs_{i}", 0.34, 0.05, (px, py, 0.03), STEEL, 24))
    z.smooth(z.cyl(f"Poseur_tp_{i}", 0.46, 0.06, (px, py, 1.08), CLOTH, 32))

# ---------------------------------------------------------------------------
# right zone — lounge + catering bar
# ---------------------------------------------------------------------------
z.box("Lounge_rug", (6.4, 5.2, 0.02), (10.0, -15.5, 0.012),
      z.m_fabric("Rug", [min(1.0, c * 1.5) for c in D["carpet"]], scale=150.0))
for s, sy in ((0, -1), (1, 1)):
    yy = -15.5 + sy * 1.9
    z.bevel(z.box(f"Sofa_seat_{s}", (3.10, 0.95, 0.42), (10.0, yy, 0.34), SOFA), 0.05)
    z.bevel(z.box(f"Sofa_back_{s}", (3.10, 0.32, 0.62), (10.0, yy + sy * 0.46, 0.72), SOFA), 0.05)
    for k in (-1, 1):
        z.bevel(z.box(f"Sofa_arm_{s}_{k}", (0.28, 0.95, 0.30),
                      (10.0 + k * 1.55, yy, 0.62), SOFA), 0.05)
z.bevel(z.box("Coffee_top", (1.70, 1.05, 0.08), (10.0, -15.5, 0.44), GOLD_HI), 0.012)
z.smooth(z.cyl("Coffee_base", 0.26, 0.42, (10.0, -15.5, 0.21), GOLD, 20))
for i, (px, py) in enumerate([(7.0, -18.0), (13.0, -18.0), (7.0, -12.9), (13.4, -12.9)]):
    z.place(PF_PLANT, (px, py, 0), rot_z=rng.random() * 3.14, name=f"LoungePlant_{i}")
# bar
z.bevel(z.box("Bar_body", (6.60, 1.30, 1.10), (12.4, -8.6, 0.55), WOOD), 0.03)
z.bevel(z.box("Bar_top", (6.80, 1.46, 0.09), (12.4, -8.6, 1.14), MARBLE), 0.012)
z.box("Bar_glow", (6.40, 0.08, 0.07), (12.4, -9.28, 0.74), GLOW)
z.bevel(z.box("Bar_backbar", (5.60, 0.44, 2.40), (13.2, -7.5, 1.20), BLACK), 0.02)
for k in range(3):
    z.box(f"Bar_shelf_{k}", (5.40, 0.36, 0.05), (13.2, -7.62, 0.75 + k * 0.62), GOLD)
for i in range(21):
    sh, col = i % 3, i // 3
    mat = GLASSM if i % 2 else z.m_plain(f"Btl{i}", (0.30 + rng.random() * 0.35, 0.08, 0.06), rough=0.25)
    z.smooth(z.cyl(f"Bottle_{i}", 0.055 + rng.random() * 0.02, 0.30 + rng.random() * 0.12,
                   (10.9 + col * 0.72, -7.62, 0.95 + sh * 0.62), mat, 12))
for i in range(6):
    z.smooth(z.cyl(f"Chafe_{i}", 0.34, 0.22, (10.0 + i * 0.86, -8.35, 1.26), GOLD_HI, 24))
for i in range(4):
    z.smooth(z.cyl(f"Stool_{i}", 0.20, 0.72, (10.4 + i * 1.15, -9.75, 0.36), STEEL, 16))
    z.smooth(z.cyl(f"StoolTop_{i}", 0.24, 0.07, (10.4 + i * 1.15, -9.75, 0.75), SOFA, 20))

# ---------------------------------------------------------------------------
# figures for scale (abstract massing — never presented as real people)
# ---------------------------------------------------------------------------
for i, (px, py) in enumerate([(-2.6, -9.2), (-8.6, -12.4), (3.4, -10.6), (12.6, -10.4),
                              (9.2, -13.2), (-5.6, -16.0), (1.6, -4.0), (-1.9, 0.6),
                              (13.2, 3.0), (-13.0, 5.4), (5.5, -6.5), (-3.2, 13.6)]):
    z.place(PF_PERSON, (px, py, 0), rot_z=rng.random() * 6.28, name=f"Figure_{i}")

# ---------------------------------------------------------------------------
# lighting + atmosphere
# ---------------------------------------------------------------------------
z.gradient_world(top=(0.008, 0.010, 0.022), bottom=(0.002, 0.002, 0.004), strength=1.0)

# ambience is deliberately LOW — an event room is dark with pools of light
z.area("Amb_room", (0, 2.0, H - 1.2), 14.0, 55, (1.00, 0.84, 0.64),
       size_y=20.0, shape="RECTANGLE", specular=0.4)
z.area("Amb_front", (0, -14.0, H - 1.2), 12.0, 55, (1.00, 0.86, 0.70),
       size_y=10.0, shape="RECTANGLE", specular=0.4)
z.area("Stage_key", (0, STAGE_Y - 5.5, 7.6), 7.0, 1500, D["beam_a"])
z.area("Stage_fill", (0, STAGE_Y + 2.0, 6.0), 10.0, 380, D["beam_b"])
# table pools — one soft downlight per table cluster, the banquet look
for _px in (-6.6, 0.0, 6.6):
    for _py in (2.6, 9.0):
        z.area(f"Pool_{_px}_{_py}", (_px, _py, H - 2.2), 5.0, 90, (1.00, 0.80, 0.58),
               specular=0.3)
# beams from the front truss — these are what read in the haze
for i, (xx, warm) in enumerate(MOVERS):
    if i % 2:
        continue
    z.spot(f"Beam_{i}", (xx, STAGE_Y - STAGE_D / 2 - 0.6, TRUSS_Z - 0.5),
           (xx * 0.42, STAGE_Y + 0.6, STAGE_H),
           14000, D["beam_a"] if warm else D["beam_b"], angle=7.5, blend=0.14, radius=0.015)
# two wide sweeps out over the audience — beams reading into the room
for _i, _x in enumerate((-6.4, 6.4)):
    z.spot(f"Sweep_{_i}", (_x, STAGE_Y - STAGE_D / 2 - 0.6, TRUSS_Z - 0.5),
           (_x * 2.4, -6.0, 1.2), 18000, D["beam_b"] if _i else D["beam_a"],
           angle=6.5, blend=0.12, radius=0.015)
for s, sx in ((0, -1), (1, 1)):
    z.area(f"Booth_wash_{s}", (sx * (W / 2 - 3.0), 2.0, 3.2), 3.0, 90, D["accent_glow"],
           rot=(0, math.radians(-70 * sx), 0), size_y=18.0, shape="RECTANGLE")
z.area("Arch_wash", (0, AY + 1.4, 4.6), 4.0, 110, D["accent_glow"])

# haze — thin through the room, denser slab over the stage where beams live
z.haze("Haze_room", (W - 1.0, L - 1.0, H - 0.6), (0, 0, (H - 0.6) / 2),
       density=0.0026, color=(0.86, 0.90, 1.00))
z.haze("Haze_stage", (STAGE_W + 4.0, STAGE_D + 8.0, 8.0), (0, STAGE_Y - 2.0, 4.0),
       density=0.0230, color=(0.90, 0.93, 1.00))

# ---------------------------------------------------------------------------
# cameras
# ---------------------------------------------------------------------------
CAMS = {
    "iso": z.camera("CAM_ISO", (0, -34.0, 23.0), (0, 6.0, 2.2), lens=24, make_active=True),
    "stage": z.camera("CAM_STAGE", (-10.6, -1.8, 2.35), (0.6, STAGE_Y + 1.2, 3.6),
                      lens=30, fstop=4.0, focus_target=(0, STAGE_Y, 3.2), make_active=False),
    "plan": z.camera("CAM_PLAN", (0, 1.0, 40.0), (0, 1.0, 0.0), lens=32, make_active=False),
    "booth": z.camera("CAM_BOOTH", (-8.4, -6.4, 2.0), (-13.4, 1.0, 2.0),
                      lens=35, fstop=2.8, make_active=False),
    "arch": z.camera("CAM_ARCH", (0.0, -20.5, 2.4), (0, 0.0, 3.0),
                     lens=30, fstop=3.5, focus_target=(0, AY, 3.4), make_active=False),
}
bpy.context.scene.camera = CAMS["iso"]

# ---------------------------------------------------------------------------
# export + optional renders
# ---------------------------------------------------------------------------
OUT = z.out_dir()
BASE = os.path.join(OUT, f"AURUM_{KEY}_v3")
print("STATS", z.stats(), flush=True)
print("EXPORT", z.export(BASE), flush=True)

for shot in SHOTS:
    cam = CAMS.get(shot)
    if not cam:
        print("no such camera:", shot, flush=True)
        continue
    path = os.path.join(OUT, f"AURUM_{KEY}_v3_{shot}.png")
    print("RENDERING", shot, flush=True)
    z.render_shot(cam, path)
    print("RENDERED", shot, path, flush=True)
print("DONE", KEY, flush=True)
