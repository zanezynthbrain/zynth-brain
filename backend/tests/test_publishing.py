"""Meta publishing: queue state machine, scheduling rules, asset hosting (offline).

Nothing here touches the network — meta.is_configured() is false without a
token, so every path runs in dry-run mode and asserts what WOULD be sent.
"""

from datetime import datetime, timedelta

import pytest

from utils import assets, publish_queue as Q
from utils.meta import (
    MAX_LEAD,
    MetaError,
    is_configured,
    platform_of,
    publish_instagram_post,
    schedule_facebook_post,
    validate_schedule_time,
)
from utils.publisher import NotApproved, compose_caption, publish_entry, readiness


def _plan(n=3):
    return {
        "brand": "ZYNTH",
        "month": "September 2026",
        "content": {"posts": [
            {"ref": f"P{i:02d}", "week": (i - 1) // 2 + 1,
             "platform": "Facebook" if i % 2 else "Instagram",
             "content_type": "static_post",
             "hook_mm": "မြန်မာ ခေါင်းစဉ်",
             "caption_mm": f"မြန်မာ စာသား {i}",
             "caption_en": f"English caption {i}",
             "hashtags": ["ZYNTH", "#Yangon"],
             "cta": "Inbox", "needs_design": False}
            for i in range(1, n + 1)
        ]},
    }


# --- Meta scheduling rules --------------------------------------------------

def test_meta_is_not_configured_without_a_token():
    ok, note = is_configured()
    assert ok is False
    assert "META_ACCESS_TOKEN" in note


def test_schedule_window_is_enforced_before_anything_is_sent():
    now = datetime.now(Q.YANGON)
    with pytest.raises(MetaError, match="10 minutes"):
        validate_schedule_time(now + timedelta(minutes=3))
    with pytest.raises(MetaError, match="6 months"):
        validate_schedule_time(now + MAX_LEAD + timedelta(days=2))
    with pytest.raises(MetaError, match="timezone-aware"):
        validate_schedule_time(datetime.now())

    ok = validate_schedule_time(now + timedelta(days=2))
    assert ok.tzinfo is not None


@pytest.mark.parametrize("label,expected", [
    ("Facebook", "facebook"), ("FB", "facebook"), ("Instagram", "instagram"),
    ("IG", "instagram"), ("instagram reels", "instagram"), ("", "facebook"),
])
def test_platform_normalisation(label, expected):
    assert platform_of(label) == expected


async def test_facebook_dry_run_reports_the_exact_request():
    when = datetime.now(Q.YANGON) + timedelta(days=1)
    result = await schedule_facebook_post("မင်္ဂလာပါ\n\nHello", when)

    assert result.ok and result.action == "would_send"
    assert result.request["published"] == "false"
    assert result.request["scheduled_publish_time"] == int(when.timestamp())
    assert "feed" in result.request["_path"]


async def test_instagram_refuses_without_a_public_url():
    result = await publish_instagram_post("caption", media_url="")
    assert result.ok is False
    assert "public image or video URL" in result.error


# --- Queue state machine ----------------------------------------------------

def test_enqueue_spreads_posts_and_starts_pending(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    start = datetime.now(Q.YANGON) + timedelta(days=3)

    added = Q.enqueue_plan(_plan(4), start=start, brand="ZYNTH")

    assert len(added) == 4
    assert all(e["state"] == "pending" for e in added)
    times = [datetime.fromisoformat(e["publish_at"]) for e in added]
    assert times == sorted(times), "posts should be queued in chronological order"
    assert all(t.hour == 19 for t in times), "default slot is 19:00 Yangon"
    # Re-queueing the same plan must not duplicate.
    assert Q.enqueue_plan(_plan(4), start=start, brand="ZYNTH") == []


def test_enqueue_rejects_naive_start(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="timezone-aware"):
        Q.enqueue_plan(_plan(1), start=datetime.now())


def test_queue_transitions_and_history(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    added = Q.enqueue_plan(_plan(2), start=datetime.now(Q.YANGON) + timedelta(days=2))
    entry_id = added[0]["id"]

    assert Q.approve(entry_id)["state"] == "approved"
    assert Q.mark_scheduled(entry_id, "123_456", "2026-09-07T19:00:00+06:30")["state"] == "scheduled"
    assert Q.get(entry_id)["meta_post_id"] == "123_456"

    other = added[1]["id"]
    assert Q.skip(other, "off-brand")["state"] == "skipped"

    counts = Q.stats()
    assert counts["scheduled"] == 1 and counts["skipped"] == 1
    assert any("approved by MD" in h["event"] for h in Q.get(entry_id)["history"])


async def test_unapproved_entries_are_never_sent(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    added = Q.enqueue_plan(_plan(1), start=datetime.now(Q.YANGON) + timedelta(days=2))

    with pytest.raises(NotApproved, match="pending"):
        await publish_entry(added[0]["id"])

    with pytest.raises(NotApproved, match="No queue entry"):
        await publish_entry("does-not-exist")


async def test_approved_facebook_entry_schedules_and_records(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    plan = _plan(1)
    plan["content"]["posts"][0]["platform"] = "Facebook"
    added = Q.enqueue_plan(plan, start=datetime.now(Q.YANGON) + timedelta(days=2))
    entry_id = added[0]["id"]
    Q.approve(entry_id)

    result = await publish_entry(entry_id)

    assert result.ok and result.action == "would_send"  # dry run, no token
    assert "မြန်မာ" in result.request["message"], "Myanmar leads the caption"


def test_caption_puts_myanmar_first_then_english_then_tags():
    caption = compose_caption({
        "caption_mm": "မြန်မာ စာသား", "caption_en": "English text",
        "hashtags": ["ZYNTH", "#Yangon"],
    })
    lines = caption.split("\n\n")
    assert lines[0] == "မြန်မာ စာသား"
    assert lines[1] == "English text"
    assert lines[2] == "#ZYNTH #Yangon", "bare tags get their hash added"


def test_readiness_blocks_instagram_without_an_asset_url():
    ready, why = readiness({"platform": "Instagram", "caption_en": "hi", "caption_mm": "ဟေး"})
    assert ready is False and "public asset URL" in why

    ready, why = readiness({"platform": "Facebook", "caption_en": "hi", "caption_mm": "ဟေး"})
    assert ready is True

    ready, why = readiness({"platform": "Facebook", "caption_en": "", "caption_mm": ""})
    assert ready is False and "no caption" in why


def test_due_instagram_picks_up_entries_missed_during_a_restart(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    plan = _plan(2)
    for post in plan["content"]["posts"]:
        post["platform"] = "Instagram"
    added = Q.enqueue_plan(plan, start=datetime.now(Q.YANGON) + timedelta(days=1))

    # Nothing due yet.
    assert Q.due_instagram() == []

    # Approve one and drag its time into the past — a restart-missed post.
    Q.approve(added[0]["id"])
    Q.reschedule(added[0]["id"], datetime.now(Q.YANGON) - timedelta(hours=3))
    due = Q.due_instagram()
    assert [e["id"] for e in due] == [added[0]["id"]]

    # A pending (unapproved) past-due entry is never picked up.
    Q.reschedule(added[1]["id"], datetime.now(Q.YANGON) - timedelta(hours=3))
    assert [e["id"] for e in Q.due_instagram()] == [added[0]["id"]]


# --- Public asset hosting ---------------------------------------------------

def test_asset_route_rejects_traversal_and_bad_extensions(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assets.ASSET_DIR.mkdir(parents=True, exist_ok=True)
    (assets.ASSET_DIR / "ok.png").write_bytes(b"\x89PNG\r\n")
    (tmp_path / "secret.env").write_text("TOKEN=abc")

    target, mime = assets.resolve_request("/assets/ok.png")
    assert target and mime == "image/png"

    for bad in ("/assets/../secret.env", "/assets/%2e%2e/secret.env",
                "/assets/nested/ok.png", "/assets/", "/other/ok.png",
                "/assets/missing.png"):
        target, _ = assets.resolve_request(bad)
        assert target is None, bad


def test_asset_token_is_required_when_set(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assets.ASSET_DIR.mkdir(parents=True, exist_ok=True)
    (assets.ASSET_DIR / "ok.png").write_bytes(b"\x89PNG\r\n")

    from config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("ZYNTH_ASSET_TOKEN", "s3cret")
    try:
        assert assets.resolve_request("/assets/ok.png")[0] is None
        assert assets.resolve_request("/assets/wrong/ok.png")[0] is None
        assert assets.resolve_request("/assets/s3cret/ok.png")[0] is not None
    finally:
        monkeypatch.delenv("ZYNTH_ASSET_TOKEN", raising=False)
        get_settings.cache_clear()


def test_publish_file_whitelists_extensions(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "art.png"
    src.write_bytes(b"\x89PNG\r\n")
    assert assets.publish_file(src).name == "art.png"

    bad = tmp_path / "payload.svg"
    bad.write_text("<svg/>")
    with pytest.raises(ValueError, match="Refusing"):
        assets.publish_file(bad)

    with pytest.raises(FileNotFoundError):
        assets.publish_file(tmp_path / "nope.png")


def test_public_url_is_empty_until_hosting_is_configured():
    assert assets.public_url("art.png") == ""
    assert "Asset hosting OFF" in assets.hosting_status()


def test_safe_name_flattens_hostile_input():
    assert assets.safe_name("../../etc/passwd") == "passwd"
    assert assets.safe_name("a b/c;d.png") == "c-d.png"
    assert assets.safe_name("") == "asset"
