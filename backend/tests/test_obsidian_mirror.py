"""The repo → Obsidian mirror (the vault the MD actually opens)."""

from pathlib import Path

from utils import obsidian as OB


def test_mirrored_docs_land_in_the_vault_obsidian_opens():
    written = OB.mirror_repo_docs()
    assert written, "nothing mirrored"
    for path in written:
        # vault/ at the repo root — NOT outputs/proposal_pool/vault/
        assert "vault/ZYNTH-OS" in str(path)
        assert "proposal_pool" not in str(path)
        assert path.is_file()


def test_mirrors_are_hidden_from_the_agent_knowledge_budget():
    """Mirrors are duplicates. The loader skips TEMPLATE-marked files, which
    keeps them out of the agents' 30k character budget."""
    for path in OB.mirror_repo_docs():
        head = path.read_text(encoding="utf-8")[:300]
        assert "<!-- TEMPLATE -->" in head, f"{path.name} would eat agent context"


def test_mirror_names_its_source_so_edits_go_to_the_right_place():
    for path in OB.mirror_repo_docs():
        text = path.read_text(encoding="utf-8")
        assert "source:" in text and "Edit the source in the repo" in text


def test_skills_index_lists_every_repo_skill():
    index = OB.skills_index_note()
    text = index.read_text(encoding="utf-8")
    skills = list((Path(__file__).resolve().parent.parent.parent / ".claude" / "skills").glob("*/SKILL.md"))
    assert f"{len(skills)} repo-versioned skills" in text
    for name in ("yadana-finance", "zb-icp", "zynth-art-director"):
        assert f"`{name}`" in text


def test_live_notes_are_carried_across_from_the_pool_vault():
    written = OB.mirror_live_notes()
    if not written:
        return  # no pool notes generated yet in this environment
    names = {p.name for p in written}
    assert any("Home" in n or "Snapshot" in n for n in names)
    assert all("Live" in str(p) for p in written)


def test_full_sync_includes_the_mirror():
    import inspect
    source = inspect.getsource(OB.full_sync)
    assert "mirror_repo_docs" in source and "mirror_live_notes" in source


def test_mirror_destinations_do_not_double_nest():
    """_OBSIDIAN is already vault/ZYNTH-OS — a destination starting with
    'ZYNTH-OS/' produced vault/ZYNTH-OS/ZYNTH-OS/. It did, once."""
    for dest in OB.MIRRORED_DOCS.values():
        assert not dest.startswith("ZYNTH-OS/"), f"{dest} nests ZYNTH-OS twice"


def test_every_mirrored_source_exists():
    """A destination pointing at a missing source silently mirrors nothing."""
    missing = [src for src in OB.MIRRORED_DOCS if not (OB._REPO / src).is_file()]
    assert not missing, f"mirror list points at files that don't exist: {missing}"


def test_latest_handoff_is_mirrored():
    assert any("2026-08-07" in src for src in OB.MIRRORED_DOCS), \
        "the handoff CLAUDE.md points at must reach Obsidian too"


def test_mirror_is_idempotent_when_the_source_has_not_changed(tmp_path):
    """A second mirror of unchanged content must not rewrite the file.

    The generated header carries a `mirrored:` timestamp. Writing it blindly
    made every mirror run dirty every mirrored note in git, which buried real
    edits in timestamp noise — 16 files churned on each test run.
    """
    from utils import obsidian

    dest = tmp_path / "note.md"
    obsidian._write_mirror(dest, "docs/thing.md", "# Body\n\nsame content\n")
    first = dest.read_text(encoding="utf-8")
    stat_before = dest.stat().st_mtime_ns

    obsidian._write_mirror(dest, "docs/thing.md", "# Body\n\nsame content\n")

    assert dest.read_text(encoding="utf-8") == first
    assert dest.stat().st_mtime_ns == stat_before, "file was rewritten unnecessarily"


def test_mirror_does_rewrite_when_the_body_changes(tmp_path):
    from utils import obsidian

    dest = tmp_path / "note.md"
    obsidian._write_mirror(dest, "docs/thing.md", "# Body\n\noriginal\n")
    obsidian._write_mirror(dest, "docs/thing.md", "# Body\n\nedited\n")

    assert "edited" in dest.read_text(encoding="utf-8")


def test_stamp_stripper_ignores_only_the_timestamp_line():
    from utils import obsidian

    a = "generated: true\nmirrored: 2026-08-07 05:48\nbody"
    b = "generated: true\nmirrored: 2026-08-08 08:43\nbody"
    assert obsidian._strip_mirror_stamp(a) == obsidian._strip_mirror_stamp(b)
    assert "generated: true" in obsidian._strip_mirror_stamp(a)
    assert "body" in obsidian._strip_mirror_stamp(a)
