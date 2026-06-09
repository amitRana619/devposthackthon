from startup_ops_agent.config import default_data_dir
from startup_ops_agent.energy_models import EnergyPriority
from startup_ops_agent.energy_repository import EnergyJsonRepository
from startup_ops_agent.energy_service import EnergyOptimizationService
from startup_ops_agent.optimizer import optimize_energy_instructions


def test_extreme_weather_and_peak_pricing_prioritizes_safety() -> None:
    service = EnergyOptimizationService(EnergyJsonRepository(default_data_dir()))

    plan = service.build_optimization_plan(
        building_id="bldg-medtech-hq",
        weather_event_id="weather-heat-dome",
        pricing_event_id="pricing-peak-surge",
        occupancy_id="occupancy-business-critical",
    )

    assert plan.primary_priority == EnergyPriority.safety
    assert plan.setpoint_c == 23.0
    assert plan.expected_load_shed_kw < 48
    assert {decision.load_id for decision in plan.load_shed} == {
        "cafeteria-cooling",
        "conference-preconditioning",
    }
    assert plan.estimated_cost_avoidance_usd == 3447.36
    assert plan.estimated_business_risk_avoided_usd == 9000.0
    assert plan.conflicts == ["extreme_weather_peak_pricing"]
    assert any("HeatRisk" in basis for basis in plan.real_world_basis)
    assert any("Critical-zone policy" in note for note in plan.compliance_notes)
    assert "weather-heat-dome" in plan.source_ids


def test_scenario_resolver_builds_heat_dome_peak_surge_plan() -> None:
    service = EnergyOptimizationService(EnergyJsonRepository(default_data_dir()))

    result = service.build_plan_from_scenario(
        "Optimize MedTech HQ during the heat dome and peak-demand surge. "
        "Prioritize critical occupants."
    )

    assert result["resolved_inputs"] == {
        "building_id": "bldg-medtech-hq",
        "weather_event_id": "weather-heat-dome",
        "pricing_event_id": "pricing-peak-surge",
        "occupancy_id": "occupancy-business-critical",
    }
    assert result["plan"].primary_priority == EnergyPriority.safety


def test_peak_pricing_on_normal_day_prioritizes_cost() -> None:
    service = EnergyOptimizationService(EnergyJsonRepository(default_data_dir()))

    plan = service.build_optimization_plan(
        building_id="bldg-medtech-hq",
        weather_event_id="weather-normal",
        pricing_event_id="pricing-peak-surge",
        occupancy_id="occupancy-low",
    )

    assert plan.primary_priority == EnergyPriority.cost
    assert plan.expected_load_shed_kw == 48.0
    assert {decision.load_id for decision in plan.load_shed} == {
        "cafeteria-cooling",
        "conference-preconditioning",
        "ev-chargers",
    }
    assert plan.estimated_cost_avoidance_usd == 7660.8
    assert plan.estimated_business_risk_avoided_usd == 0.0
    assert plan.conflicts == []


def test_simulation_returns_observability_trace() -> None:
    service = EnergyOptimizationService(EnergyJsonRepository(default_data_dir()))

    result = service.run_simulation_case("heat-dome-peak-price-critical-occupancy")

    assert result.passed is True
    assert [step.step for step in result.trace] == ["retrieve_context", "resolve_conflict"]


def test_instruction_optimizer_adds_missing_conflict_rules() -> None:
    result = optimize_energy_instructions("You are an energy assistant.")

    assert result["changed"] is True
    assert "occupant safety outranks energy cost during extreme weather" in result[
        "optimized_instruction"
    ]
