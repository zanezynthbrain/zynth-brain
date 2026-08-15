"""The outcome loop — learning from reality, not from itself."""
import pytest
from utils import outcomes as OC


def test_judge_scores_against_the_external_benchmark():
    assert OC.judge("engagement_rate", 6.0)["verdict"] == "beat"
    assert OC.judge("engagement_rate", 3.5)["verdict"] == "met"
    assert OC.judge("engagement_rate", 1.2)["verdict"] == "missed"
    assert OC.judge("nonsense_metric", 1)["verdict"] == "no_benchmark"


def test_lower_is_better_metrics_invert_correctly():
    """Budget variance: smaller is better. Getting this backwards would praise
    a 40% overrun."""
    assert OC.judge("budget_variance", 2.0)["verdict"] == "beat"
    assert OC.judge("budget_variance", 40.0)["verdict"] == "missed"


def test_every_benchmark_names_its_source():
    for metric, bench in OC.BENCHMARKS.items():
        assert bench.get("source"), f"{metric} has no source — that's a guess, not a benchmark"


def test_unverified_outcomes_never_count_toward_performance(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    OC.record_outcome("P01", "post", {"engagement_rate": 9.9})  # unverified
    assert OC.performance(verified_only=True)["count"] == 0
    OC.verify_outcome("P01")
    assert OC.performance(verified_only=True)["count"] == 1


def test_record_validates_kind_and_metrics(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="kind"):
        OC.record_outcome("X", "telepathy", {"roas": 3})
    with pytest.raises(ValueError, match="metric"):
        OC.record_outcome("X", "post", {})


def test_measured_misses_become_lessons_in_the_prompt_layer(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for i in range(3):
        OC.record_outcome(f"P{i}", "post", {"engagement_rate": 2.0}, verified=True)

    promoted = OC.promote_learnings(min_samples=3)
    assert promoted and "engagement_rate" in promoted[0]

    from utils.lessons import all_lessons
    assert any("UNDER-PERFORMANCE" in l.get("lesson", "") for l in all_lessons()), \
        "the lesson must actually reach the layer agents read"


def test_promotion_needs_enough_samples(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    OC.record_outcome("P1", "post", {"engagement_rate": 1.0}, verified=True)
    assert OC.promote_learnings(min_samples=3) == [], "one bad month is noise, not a lesson"
