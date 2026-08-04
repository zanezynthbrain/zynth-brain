"""Asset compositor — turns a design spec into a finished, brand-exact PNG.

This is where the AI/real split is enforced: a generator may supply the
background (an abstract field, a scene), but every piece of TYPE — the
headline, the Burmese, the logo, the CTA chip — is set here, in real fonts, at
real sizes, inside the brand's layout rules. That is why Myanmar renders
correctly and why 30 posts look like one brand.

Templates mirror the Design Director's system:
  Statement — one idea, maximum impact (static posts, quote cards)
  Ledger    — figures, pricing, budgets; reads as a document
  Summit    — event-grade, dark, for IGNITE and launches
  Teach     — light field for carousel/educational frames

Layout rules held automatically: 96px margins, the 4×120 gold entry rule,
bottom 220px kept clear on 4:5, Myanmar stacked below a gold divider at 1.9
line-height and never letter-spaced, one gold accent per frame.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

FONT_DIR = Path(__file__).resolve().parent.parent / "data" / "fonts"
OUT_DIR = Path("outputs/assets")

# ZYNTH palette — overridden per brand by the design system's palette block.
NAVY = (18, 32, 58)
DEEP = (13, 23, 41)
GOLD = (184, 138, 42)
OFFWHITE = (245, 243, 239)
CHARCOAL = (43, 43, 43)
SLATE = (90, 107, 133)

MARGIN = 96
CLEAR_ZONE = 220        # bottom of a 4:5 asset stays clear of feed UI

SIZES = {
    "square": (1080, 1080),
    "portrait": (1080, 1350),
    "story": (1080, 1920),
    "reel": (1080, 1920),
    "landscape": (1200, 675),
    "carousel": (1080, 1350),
}


def _hex_to_rgb(value: str, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    text = (value or "").strip().lstrip("#")
    if len(text) != 6:
        return fallback
    try:
        return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError:
        return fallback


def palette_from(design_system: dict[str, Any] | None) -> dict[str, tuple[int, int, int]]:
    """Read the brand's real hex values out of the design system, with fallbacks."""
    colours = {"navy": NAVY, "gold": GOLD, "offwhite": OFFWHITE,
               "charcoal": CHARCOAL, "slate": SLATE, "deep": DEEP}
    for entry in (design_system or {}).get("palette", []) or []:
        name = (entry.get("name") or "").lower()
        rgb = _hex_to_rgb(entry.get("hex", ""), (0, 0, 0))
        if rgb == (0, 0, 0):
            continue
        if "gold" in name or "accent" in name:
            colours["gold"] = rgb
        elif "navy" in name or "primary" in name:
            colours["navy"] = rgb
        elif "off" in name or "white" in name or "cream" in name:
            colours["offwhite"] = rgb
        elif "charcoal" in name or "black" in name:
            colours["charcoal"] = rgb
        elif "slate" in name or "grey" in name or "gray" in name:
            colours["slate"] = rgb
    return colours


def size_for(format_hint: str) -> tuple[int, int]:
    hint = (format_hint or "").lower()
    for key, size in SIZES.items():
        if key in hint:
            return size
    if "9:16" in hint:
        return SIZES["story"]
    if "1:1" in hint:
        return SIZES["square"]
    if "16:9" in hint:
        return SIZES["landscape"]
    return SIZES["portrait"]


def is_available() -> tuple[bool, str]:
    """Whether artwork can be composited here (Pillow + the vendored fonts)."""
    try:
        from PIL import ImageFont  # noqa: F401
    except ImportError:
        return False, "Pillow is not installed — add it to requirements to composite artwork."
    missing = [f for f in ("Inter-700.ttf", "NotoSansMyanmar-400.ttf") if not (FONT_DIR / f).is_file()]
    if missing:
        return False, f"Missing fonts: {', '.join(missing)}"
    return True, "Compositor ready (Inter + Noto Sans Myanmar)."


def _font(name: str, size: int):
    from PIL import ImageFont
    return ImageFont.truetype(str(FONT_DIR / name), size, layout_engine=ImageFont.Layout.RAQM)


def _latin(size: int, weight: int = 700):
    return _font(f"Inter-{weight}.ttf", size)


def _myanmar(size: int, weight: int = 400):
    return _font(f"NotoSansMyanmar-{weight}.ttf", size)


def _wrap(draw, text: str, font, max_width: int) -> list[str]:
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _field(width: int, height: int, colour, textured: bool = True, rules: bool = False):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (width, height), colour)
    if rules:
        draw = ImageDraw.Draw(img, "RGBA")
        for y in range(0, height, 45):
            draw.line([(0, y), (width, y)], fill=(255, 255, 255, 7), width=1)
    if textured:
        noise = Image.effect_noise((width, height), 6).convert("L")
        img = Image.blend(img, Image.merge("RGB", (noise, noise, noise)), 0.035)
        mask = Image.radial_gradient("L").resize((width, height)).point(lambda v: int(v * 0.32))
        img = Image.composite(Image.new("RGB", (width, height),
                                        tuple(int(c * 0.84) for c in colour)), img, mask)
    return img


def _background(width: int, height: int, colour, background: str | Path | None,
                textured: bool, rules: bool):
    """Use a generated background when one is supplied, else a procedural field."""
    if background and Path(background).is_file():
        from PIL import Image
        img = Image.open(background).convert("RGB")
        # cover-crop to the target canvas
        scale = max(width / img.width, height / img.height)
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))))
        left, top = (img.width - width) // 2, (img.height - height) // 2
        return img.crop((left, top, left + width, top + height))
    return _field(width, height, colour, textured=textured, rules=rules)


def render_asset(
    spec: dict[str, Any],
    design_system: dict[str, Any] | None = None,
    background: str | Path | None = None,
    out_dir: Path | None = None,
) -> Path:
    """Composite one design spec into a finished PNG and return its path.

    ``spec`` is a design spec from the studio: ref, format, template and
    ``on_asset_text`` {headline, subline, myanmar, cta_chip}. ``background`` is
    an optional generated image (from OpenArt) used as the field.
    """
    ok, note = is_available()
    if not ok:
        raise RuntimeError(note)
    from PIL import ImageDraw

    colours = palette_from(design_system)
    width, height = size_for(spec.get("format", "portrait"))
    template = (spec.get("template") or "Statement").lower()
    text = spec.get("on_asset_text", {}) or {}

    light = "ledger" in template or "teach" in template
    base_colour = colours["offwhite"] if light else (
        colours.get("deep", DEEP) if "summit" in template else colours["navy"])
    ink = colours["charcoal"] if light else colours["offwhite"]
    sub_ink = colours["slate"]
    gold = colours["gold"]

    img = _background(width, height, base_colour, background,
                      textured=not light, rules=not light and "summit" not in template)
    draw = ImageDraw.Draw(img, "RGBA")

    clear = CLEAR_ZONE if height > width else 150

    # Service cards carry more furniture than a statement, so the block starts
    # higher and the composition is measured from the content, not the canvas.
    items = spec.get("list_items") or []
    figures = spec.get("figures") or []
    badge = text.get("badge", "")
    y = int(height * (0.16 if (items or figures or badge) else 0.24))

    if badge:
        badge_font = _latin(22, 600)
        bw = draw.textlength(badge, font=badge_font) + 36
        bh = badge_font.size + 20
        draw.rounded_rectangle([MARGIN, y, MARGIN + bw, y + bh], radius=bh // 2,
                               fill=gold if not light else None,
                               outline=None if not light else gold, width=2)
        draw.text((MARGIN + 18, y + 8), badge, font=badge_font,
                  fill=(colours["navy"] if not light else gold))
        y += bh + 34

    # The gold entry rule — the system's signature mark.
    draw.rectangle([MARGIN, y, MARGIN + 120, y + 4], fill=gold)
    y += 44

    headline = text.get("headline", "") or spec.get("composition", "")[:60]
    head_font = _latin(64 if height > width else 58, 700)
    for line in _wrap(draw, headline, head_font, width - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=head_font, fill=ink)
        y += int(head_font.size * 1.18)

    if text.get("subline"):
        y += 18
        sub_font = _latin(30, 400)
        for line in _wrap(draw, text["subline"], sub_font, width - 2 * MARGIN):
            draw.text((MARGIN, y), line, font=sub_font, fill=sub_ink)
            y += int(sub_font.size * 1.35)

    # Inclusion list — one line per item, gold tick, generous leading.
    if items:
        y += 30
        item_font = _latin(27, 400)
        for item in items[:7]:
            draw.rectangle([MARGIN, y + 13, MARGIN + 16, y + 16], fill=gold)
            for i, line in enumerate(_wrap(draw, str(item), item_font, width - 2 * MARGIN - 40)):
                draw.text((MARGIN + 36, y), line, font=item_font, fill=ink if i == 0 else sub_ink)
                y += int(item_font.size * 1.32)
            y += 12

    # Figure row — the numbers do the selling (packages, volumes, price bands).
    if figures:
        y += 24
        column = (width - 2 * MARGIN) // max(1, min(4, len(figures)))
        fig_y = y
        for i, figure in enumerate(figures[:4]):
            fx = MARGIN + i * column
            draw.text((fx, fig_y), str(figure.get("value", "")), font=_latin(58, 700), fill=ink)
            draw.text((fx, fig_y + 74), str(figure.get("label", "")).upper(),
                      font=_latin(19, 600), fill=sub_ink)
        y = fig_y + 122

    # Price row — a single gold total line, reading as a document not a flyer.
    if spec.get("price_line"):
        y += 16
        rule_colour = (*sub_ink, 120)
        draw.line([(MARGIN, y), (width - MARGIN, y)], fill=rule_colour, width=1)
        price_font = _latin(32, 700)
        label_font = _latin(26, 400)
        draw.text((MARGIN, y + 24), spec.get("price_label", "Investment"),
                  font=label_font, fill=sub_ink)
        price = str(spec["price_line"])
        draw.text((width - MARGIN - draw.textlength(price, font=price_font), y + 20),
                  price, font=price_font, fill=gold)
        y += 78
        draw.line([(MARGIN, y), (width - MARGIN, y)], fill=rule_colour, width=1)
        y += 10

    # Myanmar never shares a line with English — it stacks below a gold divider,
    # at 1.9 line-height, never letter-spaced.
    if text.get("myanmar"):
        y += 34
        draw.rectangle([MARGIN, y, MARGIN + 90, y + 3], fill=gold)
        y += 30
        mm_font = _myanmar(32)
        for line in _wrap(draw, text["myanmar"], mm_font, width - 2 * MARGIN):
            draw.text((MARGIN, y), line, font=mm_font, fill=ink)
            y += int(32 * 1.9)

    if text.get("cta_chip"):
        chip_font = _latin(24, 600)
        label = text["cta_chip"]
        chip_w = draw.textlength(label, font=chip_font) + 52
        chip_h = chip_font.size + 28
        cy = height - clear - chip_h + 20
        outline = gold if not light else colours["navy"]
        draw.rounded_rectangle([MARGIN, cy, MARGIN + chip_w, cy + chip_h],
                               radius=chip_h // 2, outline=outline, width=2)
        draw.text((MARGIN + 26, cy + 12), label, font=chip_font, fill=outline)

    # Logo lockup — letterspaced wordmark, bottom left of the clear zone.
    logo_font = _latin(26, 700)
    lx, ly = MARGIN, height - clear + 46
    for char in "ZYNTH":
        draw.text((lx, ly), char, font=logo_font, fill=ink)
        lx += draw.textlength(char, font=logo_font) + 6

    out_dir = out_dir or OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    ref = "".join(c for c in str(spec.get("ref", "asset")) if c.isalnum() or c in "-_") or "asset"
    path = out_dir / f"{ref}_{width}x{height}.png"
    img.save(path, "PNG")
    return path


def render_plan_assets(
    plan: dict[str, Any],
    backgrounds: dict[str, str] | None = None,
    limit: int = 0,
) -> list[dict[str, Any]]:
    """Composite every design spec in a plan. Returns [{ref, path, error}]."""
    system = plan.get("design_system", {}) or {}
    specs = (plan.get("designs", {}) or {}).get("design_specs", []) or []
    if limit:
        specs = specs[:limit]
    results = []
    for spec in specs:
        ref = spec.get("ref", "?")
        try:
            path = render_asset(spec, system, (backgrounds or {}).get(ref))
            results.append({"ref": ref, "path": str(path), "error": ""})
        except Exception as exc:  # noqa: BLE001 — one bad spec must not stop the batch
            results.append({"ref": ref, "path": "", "error": str(exc)})
    return results


def attach_to_plan(plan: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    """Write rendered asset paths back onto the plan's posts, keyed by ref."""
    by_ref = {r["ref"]: r["path"] for r in results if r.get("path")}
    for post in (plan.get("content", {}) or {}).get("posts", []) or []:
        path = by_ref.get(post.get("ref"))
        if path:
            post["asset_path"] = path
    return plan


__all__ = ["render_asset", "render_plan_assets", "attach_to_plan", "palette_from",
           "size_for", "is_available", "SIZES", "FONT_DIR", "OUT_DIR"]
