"""ZYNTH 3D — shared design-direction palette table.

One source of truth for both event_scene_build.py (full ballroom) and
stage_forms.py (stage architecture studio), so a palette tweak lands in both.

Each entry drives: carpet/ground, wall dark+light, accent metal, accent glow,
LED deep+mid (which also paints the generated screen content), two beam colours,
table cloth, and stone base+vein.

Adding a direction: copy an entry, change the 12 colours, and name it after the
FEELING, not the colour ("midnight-garden", not "dark green").
"""

DIRECTIONS = {
    # gold + navy, warm wood — ZYNTH house, black-tie gala, banking/fintech
    "aurum": dict(
        carpet=(0.030, 0.045, 0.130), wall_dark=(0.115, 0.070, 0.032),
        wall_light=(0.290, 0.185, 0.090), accent=(0.83, 0.65, 0.22),
        accent_glow=(1.00, 0.76, 0.30), led_deep=(0.02, 0.09, 0.34),
        led_mid=(0.06, 0.26, 0.72), beam_a=(1.00, 0.78, 0.38),
        beam_b=(0.35, 0.55, 1.00), cloth=(0.93, 0.91, 0.86),
        marble=(0.045, 0.050, 0.075), marble_vein=(0.50, 0.47, 0.42),
    ),
    # monochrome + white light — minimal, hard-edged, tech keynote / product launch
    "obsidian": dict(
        carpet=(0.022, 0.022, 0.026), wall_dark=(0.030, 0.030, 0.034),
        wall_light=(0.105, 0.105, 0.115), accent=(0.78, 0.79, 0.82),
        accent_glow=(0.92, 0.95, 1.00), led_deep=(0.02, 0.02, 0.03),
        led_mid=(0.30, 0.34, 0.40), beam_a=(0.95, 0.97, 1.00),
        beam_b=(0.72, 0.78, 0.92), cloth=(0.10, 0.10, 0.11),
        marble=(0.030, 0.030, 0.034), marble_vein=(0.55, 0.56, 0.58),
    ),
    # emerald + brass, botanical — lush, natural, hospitality / property / lifestyle
    "emerald": dict(
        carpet=(0.020, 0.055, 0.040), wall_dark=(0.055, 0.075, 0.055),
        wall_light=(0.150, 0.190, 0.150), accent=(0.72, 0.55, 0.24),
        accent_glow=(0.95, 0.74, 0.34), led_deep=(0.01, 0.10, 0.07),
        led_mid=(0.06, 0.34, 0.24), beam_a=(0.95, 0.80, 0.42),
        beam_b=(0.35, 0.90, 0.65), cloth=(0.94, 0.93, 0.88),
        marble=(0.040, 0.055, 0.048), marble_vein=(0.52, 0.55, 0.48),
    ),
    # copper + oxblood, moody — dramatic, low-key, awards night / whisky / luxury
    "ember": dict(
        carpet=(0.075, 0.020, 0.022), wall_dark=(0.080, 0.045, 0.030),
        wall_light=(0.190, 0.115, 0.070), accent=(0.72, 0.42, 0.20),
        accent_glow=(1.00, 0.55, 0.22), led_deep=(0.14, 0.03, 0.02),
        led_mid=(0.52, 0.16, 0.06), beam_a=(1.00, 0.58, 0.26),
        beam_b=(0.90, 0.30, 0.20), cloth=(0.90, 0.86, 0.80),
        marble=(0.060, 0.038, 0.032), marble_vein=(0.48, 0.40, 0.34),
    ),
    # white + ice blue, clean — clinical, bright, pharma / medical congress
    "lumen": dict(
        carpet=(0.140, 0.155, 0.180), wall_dark=(0.300, 0.320, 0.350),
        wall_light=(0.640, 0.665, 0.700), accent=(0.62, 0.76, 0.92),
        accent_glow=(0.78, 0.90, 1.00), led_deep=(0.05, 0.14, 0.26),
        led_mid=(0.30, 0.62, 0.90), beam_a=(0.92, 0.96, 1.00),
        beam_b=(0.55, 0.78, 1.00), cloth=(0.96, 0.96, 0.97),
        marble=(0.500, 0.520, 0.545), marble_vein=(0.82, 0.84, 0.86),
    ),
}
