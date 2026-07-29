"""Roundtable discussion engine + dual-storage tests (offline)."""

import asyncio


def test_roundtable_runs_and_produces_transcript(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    from agents.roundtable import run_roundtable, summary, VOICES
    res = asyncio.run(run_roundtable("A rough draft proposal for KBZ.", kind="proposal", rounds=1))
    assert "final" in res and "score" in res
    assert res["transcript"], "there must be a discussion transcript"
    voices_in = {t["voice"] for t in res["transcript"]}
    # every named voice took part, plus the reviser and the critic
    for name, _ in VOICES:
        assert name in voices_in, f"{name} did not speak"
    assert "Reviser" in voices_in and "Critic" in voices_in
    assert isinstance(summary(res), str)


def test_dual_store_saves_github_now_drive_pending(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)
    monkeypatch.delenv("DRIVE_DELIVERABLES_FOLDER", raising=False)
    from utils import dual_store
    entry = dual_store.save_output("Q3 Plan", "# content\nbody", department="Events")
    # GitHub copy really exists on disk (this is what CI/gitsync commit)
    from pathlib import Path
    assert Path(entry["github"]).exists()
    assert "events" in entry["github"]
    # Drive is honestly pending until a service account is configured
    assert dual_store.drive_enabled() is False
    assert "pending" in entry["drive"]
    # indexed + listable
    assert dual_store.list_deliverables()[0]["title"] == "Q3 Plan"
    assert "GitHub ON" in dual_store.status_line()
