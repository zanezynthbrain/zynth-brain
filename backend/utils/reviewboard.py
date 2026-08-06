"""Review board — the QC surface where a month is checked before it's approved.

A self-contained HTML page showing every post side by side with its artwork,
its Burmese and English copy, its schedule slot, its design and motion specs,
and an automatic check list. The MD reads one page instead of scrolling a
16-row table in a Word document, and every problem is flagged in place.

Served at ``/review`` on the bot's public server, and sendable to Telegram as a
file. No external assets, no scripts from a CDN — it opens on a phone offline.

The checks are deterministic (no LLM call): they catch the specific failures
this pipeline is prone to — missing Burmese, translation artifacts, hooks too
long for the feed, designed posts with no asset, Instagram posts with no public
URL, and captions that break platform limits.
"""

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

#: Platform caption limits worth respecting (Meta's hard caps are higher, but
#: these are where the feed truncates or engagement falls off).
CAPTION_SOFT_LIMIT = 2200      # Instagram's hard cap
HOOK_FEED_LIMIT = 125          # what shows before "See more" on mobile
IG_HASHTAG_LIMIT = 30


def check_post(post: dict[str, Any]) -> list[dict[str, str]]:
    """Deterministic QC on one post. Returns [{level, message}]."""
    issues: list[dict[str, str]] = []

    def flag(level: str, message: str) -> None:
        issues.append({"level": level, "message": message})

    mm = (post.get("caption_mm") or "").strip()
    en = (post.get("caption_en") or "").strip()
    hook_mm = (post.get("hook_mm") or "").strip()
    hook = (post.get("hook") or "").strip()

    if not mm:
        flag("error", "No Burmese caption — this cannot publish to a Myanmar audience.")
    if not en:
        flag("warn", "No English caption.")
    if not hook_mm and mm:
        flag("warn", "No Burmese hook recorded — the Copy Chief did not reach this post.")

    # Translation artifacts the Myanmar ad-craft standard names explicitly.
    if mm.count("သင်") > 1:
        flag("warn", f"'သင်' appears {mm.count('သင်')}× — reads as translated. Cut all but one.")
    if "ဖြစ်ပါသည်" in mm:
        flag("warn", "'ဖြစ်ပါသည်' closing — flattens ad copy into a report.")
    if mm and any(marker in mm for marker in ("ြ", "ျ")) is False and len(mm) > 40:
        flag("info", "No medial consonants found — check this is real Myanmar text, not placeholder.")

    if len(hook) > HOOK_FEED_LIMIT:
        flag("warn", f"English hook is {len(hook)} chars — the feed cuts around {HOOK_FEED_LIMIT}.")
    if len(mm) > CAPTION_SOFT_LIMIT:
        flag("error", f"Burmese caption is {len(mm)} chars — Instagram's cap is {CAPTION_SOFT_LIMIT}.")

    tags = post.get("hashtags") or []
    if len(tags) > IG_HASHTAG_LIMIT:
        flag("error", f"{len(tags)} hashtags — Instagram allows {IG_HASHTAG_LIMIT}.")

    ctas = [c for c in (post.get("cta"), post.get("cta_mm")) if c]
    if not ctas:
        flag("warn", "No CTA.")

    if post.get("needs_design") and not post.get("asset_path"):
        flag("error", "Designed post with no artwork attached.")

    platform = (post.get("platform") or "").lower()
    if "insta" in platform and not (post.get("asset_path") or post.get("asset_url")):
        flag("error", "Instagram post with no media — Instagram cannot publish text alone.")

    return issues


_FONT_DIR = Path(__file__).resolve().parent.parent / "data" / "fonts"


def _myanmar_font_face() -> str:
    """Embed Noto Sans Myanmar so Burmese renders on any device, online or not.

    Without this the board opens with disconnected glyphs on machines that have
    no Myanmar font — which is most laptops, and every headless browser. A QC
    tool that misrenders the thing being checked is worse than no QC tool.
    """
    import base64

    faces = []
    for weight, name in ((400, "NotoSansMyanmar-400.ttf"), (700, "NotoSansMyanmar-700.ttf")):
        path = _FONT_DIR / name
        if not path.is_file():
            continue
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        faces.append(
            f"@font-face{{font-family:'ZynthMyanmar';font-style:normal;font-weight:{weight};"
            f"font-display:swap;src:url(data:font/ttf;base64,{data}) format('truetype');}}"
        )
    return "".join(faces)


def _state_badge(entry: dict[str, Any]) -> tuple[str, str]:
    state = entry.get("state", "")
    return {
        "pending": ("Pending", "warn"),
        "approved": ("Approved", "ok"),
        "scheduled": ("Scheduled at Meta", "ok"),
        "published": ("Published", "ok"),
        "skipped": ("Skipped", "muted"),
        "failed": ("Failed", "error"),
    }.get(state, (state or "Draft", "muted"))


def _img_tag(post: dict[str, Any]) -> str:
    """Embed the artwork inline so the board works offline and in Telegram."""
    path = post.get("asset_path")
    if not path or not Path(path).is_file():
        return '<div class="noart">No artwork yet</div>'
    import base64
    data = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    suffix = Path(path).suffix.lstrip(".").lower()
    mime = "image/png" if suffix == "png" else f"image/{suffix}"
    return f'<img src="data:{mime};base64,{data}" alt="{html.escape(post.get("ref", ""))}">'


def render(plan: dict[str, Any], queue: list[dict[str, Any]] | None = None) -> str:
    """Build the review board HTML for a content plan."""
    content = plan.get("content", {}) or {}
    posts = content.get("posts", []) or []
    designs = {s.get("ref"): s for s in (plan.get("designs", {}) or {}).get("design_specs", []) or []}
    motions = {v.get("ref"): v for v in (plan.get("motion", {}) or {}).get("videos", []) or []}
    queue_by_ref = {e.get("ref"): e for e in (queue or [])}
    ratio = plan.get("ratio", {}) or {}
    credits = plan.get("credits", {}) or {}

    total_errors = total_warns = 0
    cards = []
    for post in posts:
        ref = post.get("ref", "")
        entry = queue_by_ref.get(ref, {})
        merged = {**post, **{k: v for k, v in entry.items() if v}}
        issues = check_post(merged)
        total_errors += sum(1 for i in issues if i["level"] == "error")
        total_warns += sum(1 for i in issues if i["level"] == "warn")

        label, tone = _state_badge(entry) if entry else ("Draft", "muted")
        design = designs.get(ref, {})
        motion = motions.get(ref, {})

        spec_bits = []
        if design:
            on_asset = (design.get("on_asset_text") or {}).get("headline", "")
            spec_bits.append(
                f"<b>Design</b> · {html.escape(design.get('format', ''))} · "
                f"{html.escape(design.get('template', ''))}<br>"
                f"<span class='muted'>On asset: {html.escape(on_asset)}</span>"
            )
        if motion:
            beats = len(motion.get("beat_sheet", []) or [])
            spec_bits.append(
                f"<b>Motion</b> · {html.escape(str(motion.get('duration_seconds', '')))}s · "
                f"{beats} beats<br><span class='muted'>Hook: "
                f"{html.escape(motion.get('hook_frame', ''))}</span>"
            )

        issue_html = "".join(
            f'<li class="{i["level"]}">{html.escape(i["message"])}</li>' for i in issues
        ) or '<li class="ok">All checks passed</li>'

        when = (entry.get("publish_at") or "")[:16].replace("T", " ")
        cards.append(f"""
        <article class="card">
          <div class="art">{_img_tag(merged)}</div>
          <div class="body">
            <header>
              <span class="ref">{html.escape(ref)}</span>
              <span class="pill">{html.escape(post.get('platform', ''))}</span>
              <span class="pill">{html.escape(post.get('content_type', ''))}</span>
              <span class="pill">{html.escape(post.get('pillar', ''))}</span>
              <span class="badge {tone}">{html.escape(label)}</span>
              {f'<span class="when">{html.escape(when)} Yangon</span>' if when else ''}
            </header>
            <div class="copy">
              <div class="mm"><h4>မြန်မာ</h4><p>{html.escape(merged.get('caption_mm', ''))}</p></div>
              <div class="en"><h4>English</h4><p>{html.escape(merged.get('caption_en', ''))}</p></div>
            </div>
            <div class="tags">{html.escape(' '.join(merged.get('hashtags', []) or []))}</div>
            {f'<div class="specs">{"<br><br>".join(spec_bits)}</div>' if spec_bits else ''}
            <ul class="checks">{issue_html}</ul>
          </div>
        </article>""")

    verdict = (
        f'<span class="error">{total_errors} blocking</span>' if total_errors
        else '<span class="ok">Nothing blocking</span>'
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(str(plan.get('brand', 'Brand')))} — {html.escape(str(plan.get('month', '')))} review</title>
<style>
  {_myanmar_font_face()}
  :root {{ --navy:#12203A; --gold:#B88A2A; --off:#F5F3EF; --slate:#5A6B85; --err:#B3261E; --warn:#8A6100; --ok:#1B5E20; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--off); color:var(--navy);
         font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }}
  .wrap {{ max-width:1080px; margin:0 auto; padding:24px 16px 64px; }}
  h1 {{ font-size:26px; margin:0 0 4px; }}
  .sub {{ color:var(--slate); margin:0 0 20px; }}
  .stats {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:24px; }}
  .stat {{ background:#fff; border:1px solid #e3ded5; border-radius:10px; padding:10px 14px; }}
  .stat b {{ display:block; font-size:19px; }}
  .stat span {{ color:var(--slate); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }}
  .card {{ display:flex; gap:18px; background:#fff; border:1px solid #e3ded5; border-radius:14px;
           padding:16px; margin-bottom:16px; }}
  .art {{ flex:0 0 200px; }}
  .art img {{ width:100%; border-radius:8px; display:block; }}
  .noart {{ width:100%; aspect-ratio:4/5; border:1px dashed #cfc7b8; border-radius:8px;
            display:grid; place-items:center; color:var(--slate); font-size:13px; text-align:center; padding:8px; }}
  .body {{ flex:1; min-width:0; }}
  header {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:10px; }}
  .ref {{ font-weight:700; }}
  .pill {{ background:#f1ede5; border-radius:99px; padding:2px 10px; font-size:12px; color:var(--slate); }}
  .badge {{ border-radius:99px; padding:2px 10px; font-size:12px; font-weight:600; }}
  .badge.ok {{ background:#e6f2e8; color:var(--ok); }}
  .badge.warn {{ background:#fbf0d8; color:var(--warn); }}
  .badge.error {{ background:#fbe4e2; color:var(--err); }}
  .badge.muted {{ background:#eee; color:var(--slate); }}
  .when {{ margin-left:auto; color:var(--slate); font-size:12px; }}
  .copy {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  .copy h4 {{ margin:0 0 4px; font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:var(--slate); }}
  .copy p {{ margin:0; white-space:pre-wrap; }}
  .mm p, .mm h4 {{ font-family:'ZynthMyanmar',"Noto Sans Myanmar","Pyidaungsu",sans-serif; }}
  .mm p {{ font-size:16px; line-height:1.9; }}
  .tags {{ color:var(--slate); font-size:13px; margin-top:10px; }}
  .specs {{ margin-top:12px; padding:10px 12px; background:#faf8f4; border-left:3px solid var(--gold);
            border-radius:0 8px 8px 0; font-size:13px; }}
  .muted {{ color:var(--slate); }}
  .checks {{ margin:12px 0 0; padding-left:18px; font-size:13px; }}
  .checks li.error {{ color:var(--err); }}
  .checks li.warn {{ color:var(--warn); }}
  .checks li.ok {{ color:var(--ok); }}
  .checks li.info {{ color:var(--slate); }}
  @media (max-width:760px) {{ .card {{ flex-direction:column; }} .art {{ flex:auto; max-width:260px; }}
                              .copy {{ grid-template-columns:1fr; }} }}
  @media (prefers-color-scheme: dark) {{
    body {{ background:#0f1622; color:#e9e6df; }}
    .card,.stat {{ background:#16202f; border-color:#26334a; }}
    .pill {{ background:#1e2a3d; }} .specs {{ background:#131d2b; }}
    .noart {{ border-color:#2c3a52; }}
  }}
</style></head><body><div class="wrap">
  <h1>{html.escape(str(plan.get('brand', 'Brand')))} — {html.escape(str(plan.get('month', '')))}</h1>
  <p class="sub">Content &amp; design review · generated {datetime.now():%d %b %Y %H:%M} · {verdict}</p>
  <div class="stats">
    <div class="stat"><b>{ratio.get('posts_planned', len(posts))}</b><span>posts</span></div>
    <div class="stat"><b>{html.escape(str(ratio.get('design_ratio', '—')))}</b><span>content:design</span></div>
    <div class="stat"><b>{ratio.get('short_videos', 0)}</b><span>videos</span></div>
    <div class="stat"><b>{ratio.get('boosted', 0)}</b><span>to boost</span></div>
    <div class="stat"><b>{credits.get('total_credits', 0)}</b><span>credits planned</span></div>
    <div class="stat"><b>{total_errors}</b><span>blocking issues</span></div>
    <div class="stat"><b>{total_warns}</b><span>warnings</span></div>
  </div>
  {''.join(cards)}
</div></body></html>"""


def write(plan: dict[str, Any], queue: list[dict[str, Any]] | None = None,
          out: str | Path = "") -> Path:
    """Render the board to a file and return the path."""
    path = Path(out) if out else Path("outputs/review") / (
        f"{str(plan.get('brand', 'brand')).replace(' ', '_')}_"
        f"{str(plan.get('month', '')).replace(' ', '_')}_review.html"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(plan, queue), encoding="utf-8")
    return path


def summary(plan: dict[str, Any]) -> dict[str, int]:
    """Counts for a quick text report, without rendering the page."""
    posts = (plan.get("content", {}) or {}).get("posts", []) or []
    errors = warns = 0
    for post in posts:
        for issue in check_post(post):
            if issue["level"] == "error":
                errors += 1
            elif issue["level"] == "warn":
                warns += 1
    return {"posts": len(posts), "errors": errors, "warnings": warns}


def load_plan(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


__all__ = ["check_post", "render", "write", "summary", "load_plan",
           "CAPTION_SOFT_LIMIT", "HOOK_FEED_LIMIT", "IG_HASHTAG_LIMIT"]
