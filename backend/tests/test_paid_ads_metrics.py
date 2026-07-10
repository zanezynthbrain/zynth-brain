from agents.paid_ads import analyze_performance_csv


def test_analyze_performance_csv_computes_roas_per_campaign():
    csv_text = "campaign,spend,revenue\nA,100,500\nB,200,100\n"
    metrics = analyze_performance_csv(csv_text)

    assert metrics["total_spend"] == 300.0
    assert metrics["total_revenue"] == 600.0
    assert metrics["overall_roas"] == 2.0
    assert metrics["campaigns"][0]["campaign"] == "A"  # sorted by ROAS desc
    assert metrics["campaigns"][0]["roas"] == 5.0
    assert metrics["campaigns"][1]["roas"] == 0.5


def test_analyze_performance_csv_handles_empty_input():
    metrics = analyze_performance_csv("")
    assert metrics["campaigns"] == []
    assert metrics["overall_roas"] == 0.0
