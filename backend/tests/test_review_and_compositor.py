"""QC review board checks and the brand asset compositor (offline)."""

import pytest

from utils import compositor as C
from utils import reviewboard as RB


def _post(**over):
    base = {
        "ref": "P01", "platform": "Facebook", "content_type": "static_post",
        "hook": "A short hook", "hook_mm": "မြန်မာ ခေါင်းစဉ်",
        "caption_en": "English caption", "caption_mm": "မြန်မာ စာသား ဖြစ်ပြီး ရှင်းလင်းပါတယ်",
        "hashtags": ["ZYNTH"], "cta": "Inbox", "needs_design": False,
    }
    base.update(over)
    return base


# --- Deterministic QC checks ------------------------------------------------

def test_clean_post_passes_every_check():
    assert RB.check_post(_post()) == []


def test_missing_burmese_is_blocking():
    issues = RB.check_post(_post(caption_mm=""))
    assert any(i["level"] == "error" and "No Burmese" in i["message"] for i in issues)


def test_translation_artifacts_are_flagged():
    mm = "သင် ဒီအရာကို သင် ကြိုက်မယ်လို့ ထင်ပါတယ်။ ဒါဟာ ကောင်းမွန်တဲ့ အရာ ဖြစ်ပါသည်"
    issues = RB.check_post(_post(caption_mm=mm))
    messages = " ".join(i["message"] for i in issues)
    assert "သင်" in messages and "ဖြစ်ပါသည်" in messages


def test_platform_limits_are_enforced():
    long_hook = RB.check_post(_post(hook="x" * (RB.HOOK_FEED_LIMIT + 5)))
    assert any("feed cuts" in i["message"] for i in long_hook)

    too_many = RB.check_post(_post(hashtags=["t"] * (RB.IG_HASHTAG_LIMIT + 1)))
    assert any(i["level"] == "error" and "hashtags" in i["message"] for i in too_many)

    too_long = RB.check_post(_post(caption_mm="မ" * (RB.CAPTION_SOFT_LIMIT + 1)))
    assert any(i["level"] == "error" and "cap" in i["message"] for i in too_long)


def test_missing_artwork_blocks_designed_and_instagram_posts():
    designed = RB.check_post(_post(needs_design=True))
    assert any("no artwork" in i["message"].lower() for i in designed)

    ig = RB.check_post(_post(platform="Instagram"))
    assert any(i["level"] == "error" and "cannot publish text alone" in i["message"] for i in ig)


def test_no_cta_is_a_warning_not_a_block():
    issues = RB.check_post(_post(cta=""))
    levels = {i["level"] for i in issues if "CTA" in i["message"]}
    assert levels == {"warn"}


# --- Board rendering --------------------------------------------------------

def _plan():
    return {
        "brand": "ZYNTH", "month": "September 2026",
        "content": {"posts": [_post(), _post(ref="P02", caption_mm="", platform="Instagram")]},
        "designs": {"design_specs": [{"ref": "P01", "format": "portrait", "template": "Statement",
                                      "on_asset_text": {"headline": "Twelve agents."}}]},
        "motion": {"videos": [{"ref": "P02", "duration_seconds": 20,
                               "hook_frame": "type snaps on", "beat_sheet": [{}, {}, {}]}]},
        "ratio": {"posts_planned": 2, "design_ratio": "1:2", "short_videos": 1, "boosted": 0},
        "credits": {"total_credits": 640},
    }


def test_board_renders_self_contained_html_with_the_findings():
    html = RB.render(_plan())

    assert html.startswith("<!doctype html>")
    assert "ZYNTH — September 2026" in html
    assert "No Burmese caption" in html, "the board must show what's broken"
    assert "640" in html and "1:2" in html
    # Self-contained: every url()/src/href must be inline data, and no scripts.
    import re
    external = re.findall(r'(?:url\(|src=["\']|href=["\'])(?!data:|#)([^"\')]+)', html)
    assert external == [], f"board references external resources: {external}"
    assert "<script" not in html.lower()
    assert "@font-face" in html and "ZynthMyanmar" in html, "Myanmar font is embedded"


def test_board_merges_queue_state_over_the_plan():
    queue = [{"ref": "P01", "state": "scheduled", "publish_at": "2026-09-07T19:00:00+06:30"}]
    html = RB.render(_plan(), queue=queue)
    assert "Scheduled at Meta" in html and "2026-09-07 19:00" in html


def test_summary_counts_without_rendering():
    counts = RB.summary(_plan())
    assert counts["posts"] == 2 and counts["errors"] >= 1


def test_board_writes_to_disk(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    path = RB.write(_plan())
    assert path.is_file() and path.read_text(encoding="utf-8").startswith("<!doctype")


# --- Compositor -------------------------------------------------------------

def test_compositor_is_available_with_vendored_fonts():
    ok, note = C.is_available()
    assert ok, note
    assert "Noto Sans Myanmar" in note


@pytest.mark.parametrize("hint,expected", [
    ("square 1080x1080", (1080, 1080)),
    ("portrait 4:5", (1080, 1350)),
    ("story", (1080, 1920)),
    ("landscape 16:9", (1200, 675)),
    ("", (1080, 1350)),
])
def test_size_mapping(hint, expected):
    assert C.size_for(hint) == expected


def test_palette_is_read_from_the_brand_system():
    system = {"palette": [
        {"name": "Brand Gold", "hex": "#FFCC00"},
        {"name": "Primary Navy", "hex": "#001133"},
        {"name": "Broken", "hex": "not-a-hex"},
    ]}
    colours = C.palette_from(system)
    assert colours["gold"] == (255, 204, 0)
    assert colours["navy"] == (0, 17, 51)
    assert colours["offwhite"] == C.OFFWHITE  # untouched fallback


def test_render_asset_produces_a_branded_png(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from PIL import Image

    spec = {
        "ref": "P01", "format": "portrait 1080×1350", "template": "Statement",
        "on_asset_text": {
            "headline": "Twelve agents. One human signs.",
            "subline": "The brief is on the desk at 5:30am.",
            "myanmar": "အေးဂျင့် ၁၂ ခု။ လူတစ်ယောက်က အတည်ပြုသည်။",
            "cta_chip": "Follow",
        },
    }
    path = C.render_asset(spec, {"palette": [{"name": "Gold", "hex": "#B88A2A"}]})

    assert path.is_file() and path.name == "P01_1080x1350.png"
    with Image.open(path) as img:
        assert img.size == (1080, 1350)
        # A dark Statement field, not a blank canvas.
        assert sum(img.convert("RGB").getpixel((20, 20))) < 250


def test_render_plan_assets_reports_per_spec_and_attaches_paths(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    plan = {
        "design_system": {},
        "designs": {"design_specs": [
            {"ref": "P01", "format": "square", "template": "Statement",
             "on_asset_text": {"headline": "One"}},
            {"ref": "P02", "format": "portrait", "template": "Ledger",
             "on_asset_text": {"headline": "Two"}},
        ]},
        "content": {"posts": [{"ref": "P01"}, {"ref": "P02"}, {"ref": "P03"}]},
    }

    results = C.render_plan_assets(plan)
    assert len(results) == 2 and all(r["path"] and not r["error"] for r in results)

    C.attach_to_plan(plan, results)
    posts = {p["ref"]: p for p in plan["content"]["posts"]}
    assert posts["P01"]["asset_path"].endswith("P01_1080x1080.png")
    assert "asset_path" not in posts["P03"], "posts without a spec stay untouched"
