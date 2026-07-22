"""Tests for the BD autopilot outreach layer (pure logic — no network/file IO)."""

from utils import apollo_enrich, outreach


def test_draft_email_is_personalised():
    p = {
        "company": "ATOM Myanmar",
        "contact_name": "Aung Aung",
        "marketing_gap": "A rebrand needs a consistent creative platform",
        "zynth_approach": "Pitch a brand-platform + campaign system to carry the new identity.",
        "service_fit": "brand + campaigns",
    }
    subject, body = outreach.draft_email(p)
    assert "ATOM Myanmar" in subject
    assert "Aung," in body  # greets by first name
    assert "brand-platform" in body  # uses the tailored approach
    assert "ZYNTH" in body


def test_draft_email_handles_missing_contact():
    subject, body = outreach.draft_email({"company": "KBZ Bank"})
    assert "KBZ Bank" in subject
    assert body.startswith("Hello,")  # no name → neutral greeting


def test_apollo_locked_emails_are_dropped():
    assert apollo_enrich._looks_locked("email_not_unlocked@apollo.io")
    assert apollo_enrich._looks_locked("")
    assert apollo_enrich._looks_locked("someone@domain.com")
    assert not apollo_enrich._looks_locked("real.person@kbzbank.com")


def test_apollo_title_filters_from_role_hint():
    titles = apollo_enrich._titles_for("Head of Marketing / Brand Manager")
    assert any("Marketing" in t for t in titles)
    # empty hint still returns sensible defaults
    assert apollo_enrich._titles_for("")


def test_apollo_inert_without_key(monkeypatch):
    monkeypatch.delenv("APOLLO_API_KEY", raising=False)
    assert apollo_enrich.is_configured() is False
