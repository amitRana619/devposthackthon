from startup_ops_agent.evaluation import run_evaluations


def test_evaluation_harness_passes_baseline_cases() -> None:
    report = run_evaluations()

    assert report.failed == 0
    assert {result.name for result in report.results} == {
        "instruction_contract",
        "track2_multi_agent_mandates",
        "energy_extreme_weather_peak_pricing_simulation",
        "energy_b2b_business_impact",
    }
