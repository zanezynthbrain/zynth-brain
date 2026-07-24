"""Cost audit + named-consumer registry tests (offline)."""

from utils import costaudit


def test_every_scheduled_job_has_a_consumer():
    for j in costaudit.SCHEDULED_JOBS:
        assert j.get("consumer"), f"{j['id']} has no named consumer"
        assert j.get("cadence") and j.get("purpose")


def test_audit_text_renders_offline():
    txt = costaudit.audit_text()
    assert "Cost Audit" in txt
    assert "cost per approved artifact" in txt
    assert "named-consumer" in txt.lower()
