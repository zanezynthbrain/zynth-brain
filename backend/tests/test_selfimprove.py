"""Self-improvement loop tests — mistakes log, lessons store, ImproverAgent (offline)."""

import asyncio


def test_mistakes_record_and_digest(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils import mistakes
    mistakes.record("audit", "structuring failed", "400", "error")
    mistakes.record("command", "push failed", "TimeoutError")
    r = mistakes.recent(10)
    assert len(r) == 2 and r[0]["area"] == "command"  # newest first
    assert "structuring failed" in mistakes.digest(10)
    assert mistakes.stats()["total"] == 2


def test_lessons_add_dedup_and_knowledge_injection(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    # point the knowledge dir at a temp location so we don't touch the repo file
    import utils.knowledge as kb
    kdir = tmp_path / "knowledge"
    kdir.mkdir()
    monkeypatch.setattr(kb, "KNOWLEDGE_DIR", kdir)
    from utils import lessons
    assert lessons.add("finance", "Never quote below the 35% margin floor.") is True
    assert lessons.add("finance", "never quote below the 35% margin floor") is False  # dedup
    assert lessons.add("comms", "Lead with the decision, not the detail.") is True
    assert len(lessons.all_lessons()) == 2
    # the markdown was written and is picked up by the knowledge loader
    md = (kdir / "01_learned_lessons.md")
    assert md.exists() and "35% margin floor" in md.read_text(encoding="utf-8")
    block = kb.load_knowledge(force=True)
    assert "Learned Lessons" in block and "Lead with the decision" in block


def test_improver_review_offline(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from utils.llm_client import LLMClient
    from agents.improver import ImproverAgent, caption
    agent = ImproverAgent(LLMClient())  # mock mode (no API key in tests)
    data = asyncio.run(agent.review())
    for k in ("health_score", "self_assessment", "recurring_mistakes", "lessons", "improvements"):
        assert k in data, f"missing {k}"
    # caption never raises on a schema-shaped object
    assert isinstance(caption(data), str)


def test_improve_command_is_whitelisted():
    from utils.cmdqueue import ALLOWED
    assert "improve" in ALLOWED
