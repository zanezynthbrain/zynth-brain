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
