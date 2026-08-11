"""Proposal library — the reading layer over the pool.

75 proposals in JSON that nobody can open are worth nothing, so these tests
care about one thing: can the dashboard find, filter and open a real proposal.
"""

from __future__ import annotations

import json
import pytest

from utils import proposal_library as PL


@pytest.fixture
def pool(tmp_path, monkeypatch):
    idx = [
        {"proposal_id": "aaa", "title": "Gen Z Money", "type": "Seasonal Campaign",
         "industry": "Banking & Finance", "market": "MM", "month": "July",
         "created_at": "2026-07-12T09:00:00", "file": "banking/july.json"},
        {"proposal_id": "bbb", "title": "Crunch Launch", "type": "Product Launch",
         "industry": "F&B & Restaurant", "market": "SG", "month": "August",
         "created_at": "2026-08-01T09:00:00", "file": "fandb/august.json"},
    ]
    (tmp_path / "banking").mkdir(parents=True)
    (tmp_path / "fandb").mkdir(parents=True)
    (tmp_path / "index.json").write_text(json.dumps(idx))
    (tmp_path / "banking" / "july.json").write_text(json.dumps(
        [{"proposal_id": "aaa", "objective": "Teach Gen Z to save",
          "budget_range": "20-30M MMK", "key_activities": ["workshops", "reels"]}]))
    (tmp_path / "fandb" / "august.json").write_text(json.dumps({"proposals": [
        {"proposal_id": "bbb", "objective": "Launch the crunch"}]}))

    monkeypatch.setattr(PL, "_POOL", tmp_path)
    monkeypatch.setattr(PL, "_INDEX", tmp_path / "index.json")
    monkeypatch.setattr(PL, "_DELIVERABLES", tmp_path / "deliverables" / "proposals")
    PL._sector_file.cache_clear()
    yield tmp_path
    PL._sector_file.cache_clear()


def test_index_is_newest_first(pool):
    assert [r["proposal_id"] for r in PL.index()] == ["bbb", "aaa"]


def test_open_joins_the_stub_to_the_full_body(pool):
    row = PL.full("aaa")
    assert row["title"] == "Gen Z Money"          # from the index
    assert row["objective"] == "Teach Gen Z to save"   # from the sector file
    assert row["budget_range"] == "20-30M MMK"


def test_open_handles_both_pool_file_shapes(pool):
    """Sector files are sometimes a bare list, sometimes {"proposals": [...]}."""
    assert PL.full("bbb")["objective"] == "Launch the crunch"


def test_open_unknown_id_returns_none(pool):
    assert PL.full("zzz") is None


def test_search_filters_by_text_sector_and_market(pool):
    assert len(PL.search()) == 2
    assert [r["proposal_id"] for r in PL.search(q="crunch")] == ["bbb"]
    assert [r["proposal_id"] for r in PL.search(market="MM")] == ["aaa"]
    assert PL.search(industry="F&B & Restaurant")[0]["proposal_id"] == "bbb"
    assert PL.search(q="crunch", market="MM") == []      # filters combine


def test_facets_only_offer_values_that_exist(pool):
    f = PL.facets()
    assert f["market"] == ["MM", "SG"]
    assert "Banking & Finance" in f["industry"]
    assert "" not in f["industry"]


def test_stats_counts_by_sector_and_market(pool):
    s = PL.stats()
    assert s["total"] == 2 and s["sectors"] == 2
    assert s["by_market"] == {"MM": 1, "SG": 1}
    assert s["latest"] == "2026-08-01"


def test_api_list_and_open(pool):
    payload, status = PL.handle_api({"action": "list"})
    assert status == 200 and payload["stats"]["total"] == 2
    assert payload["facets"]["market"] == ["MM", "SG"]

    payload, status = PL.handle_api({"action": "open", "id": "aaa"})
    assert status == 200 and payload["proposal"]["objective"] == "Teach Gen Z to save"


def test_api_open_missing_is_404_and_bad_action_is_400(pool):
    assert PL.handle_api({"action": "open", "id": "ghost"})[1] == 404
    assert PL.handle_api({"action": "delete_everything"})[1] == 400


def test_a_corrupt_pool_file_does_not_break_the_library(pool):
    (pool / "index.json").write_text("{ not json")
    assert PL.index() == []
    assert PL.stats()["total"] == 0


def test_library_reads_the_real_pool():
    """Against the committed pool — the dashboard must show actual proposals."""
    PL._sector_file.cache_clear()
    s = PL.stats()
    assert s["total"] > 50, f"expected the real library, got {s['total']}"
    first = PL.index()[0]
    assert PL.full(first["proposal_id"]) is not None
