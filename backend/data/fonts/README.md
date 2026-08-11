<!-- TEMPLATE -->
<!-- Not knowledge — this marker keeps the KB loader out of this folder. -->

# Fonts shipped with the bot

These are vendored deliberately: the container has no Myanmar font, so without
them every Burmese asset and every review board renders as broken, disconnected
glyphs. They are used by `utils/compositor.py` (artwork) and embedded into
`utils/reviewboard.py` output (QC pages that must be readable on any device).

| File | Family | Use |
|---|---|---|
| `NotoSansMyanmar-400.ttf` / `-700.ttf` | Noto Sans Myanmar | All Burmese text. Pyidaungsu-compatible Unicode — never Zawgyi. |
| `Inter-400/600/700.ttf` | Inter | Latin headline and body, standing in for ZYNTH's geometric sans until a licensed family is confirmed. |

**Licence:** both families are released under the SIL Open Font License 1.1,
which permits redistribution alongside software. Full text:
https://openfontlicense.org — the fonts are unmodified copies from Google Fonts.

**Rendering rules** (see `knowledge/26_myanmar_ad_craft.md`): Myanmar at 1.9
line-height minimum, ~15% larger optical size than the Latin, never
letter-spaced, never sharing a line with English, and never generated inside an
AI image model.
