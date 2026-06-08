from __future__ import annotations

import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from startup_ops_agent.config import default_data_dir, load_settings
from startup_ops_agent.energy_repository import EnergyJsonRepository
from startup_ops_agent.energy_service import EnergyOptimizationService
from startup_ops_agent.instructions import build_agent_instruction, evaluate_instruction_contract


@dataclass(frozen=True)
class EvaluationResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class EvaluationReport:
    total: int
    passed: int
    failed: int
    results: list[EvaluationResult]

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "results": [result.__dict__ for result in self.results],
        }


def _copy_data_dir(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        if path.is_file():
            shutil.copy(path, target / path.name)


def _result(name: str, passed: bool, detail: str) -> EvaluationResult:
    return EvaluationResult(name=name, passed=passed, detail=detail)


def _evaluate_instruction_contract() -> EvaluationResult:
    instruction = build_agent_instruction(load_settings())
    missing = evaluate_instruction_contract(instruction)
    return _result(
        "instruction_contract",
        not missing,
        "Instruction includes required energy tool trajectory and safety clauses."
        if not missing
        else f"Missing instruction phrases: {missing}",
    )


def _evaluate_track2_mandates() -> EvaluationResult:
    from startup_ops_agent.agent import root_agent

    sub_agent_names = {agent.name for agent in root_agent.sub_agents}
    expected = {
        "weather_pricing_grounding_agent",
        "comfort_cost_conflict_agent",
        "energy_action_governance_agent",
    }
    if sub_agent_names != expected:
        return _result(
            "track2_multi_agent_mandates",
            False,
            f"Expected ADK sub-agents {sorted(expected)}, got {sorted(sub_agent_names)}.",
        )
    if load_settings().model == "":
        return _result(
            "track2_multi_agent_mandates",
            False,
            "Gemini model configuration is empty.",
        )
    return _result(
        "track2_multi_agent_mandates",
        True,
        "ADK root agent coordinates simulation-grounded conflict and governance agents.",
    )


def _evaluate_energy_simulation(service: EnergyOptimizationService) -> EvaluationResult:
    results = service.run_all_simulations()
    failed = [result for result in results if not result.passed]
    if failed:
        return _result(
            "energy_extreme_weather_peak_pricing_simulation",
            False,
            f"Failed simulation cases: {[result.case_id for result in failed]}.",
        )
    critical = next(
        result
        for result in results
        if result.case_id == "heat-dome-peak-price-critical-occupancy"
    )
    has_trace = [step.step for step in critical.trace] == ["retrieve_context", "resolve_conflict"]
    if critical.plan.primary_priority.value != "safety" or not has_trace:
        return _result(
            "energy_extreme_weather_peak_pricing_simulation",
            False,
            "Critical rare-event case did not prioritize safety with observability trace.",
        )
    return _result(
        "energy_extreme_weather_peak_pricing_simulation",
        True,
        "Synthetic rare-event simulation prioritizes safety and emits trace steps.",
    )


def _evaluate_energy_business_impact(service: EnergyOptimizationService) -> EvaluationResult:
    plan = service.build_optimization_plan(
        building_id="bldg-medtech-hq",
        weather_event_id="weather-heat-dome",
        pricing_event_id="pricing-peak-surge",
        occupancy_id="occupancy-business-critical",
    )
    shed_load_ids = {decision.load_id for decision in plan.load_shed}
    expected_loads = {"cafeteria-cooling", "conference-preconditioning"}
    if shed_load_ids != expected_loads:
        return _result(
            "energy_b2b_business_impact",
            False,
            "Expected non-critical shed loads "
            f"{sorted(expected_loads)}, got {sorted(shed_load_ids)}.",
        )
    if (
        plan.estimated_cost_avoidance_usd <= 0
        or plan.estimated_business_risk_avoided_usd <= 0
    ):
        return _result(
            "energy_b2b_business_impact",
            False,
            "Plan did not include both cost avoidance and protected business risk impact.",
        )
    return _result(
        "energy_b2b_business_impact",
        True,
        "Rare-event plan reports load-level shedding, cost avoidance, and protected risk.",
    )


def run_evaluations(data_dir: Path | None = None) -> EvaluationReport:
    source = data_dir or default_data_dir()
    with tempfile.TemporaryDirectory(prefix="startup-ops-eval-") as temp_dir:
        isolated_data_dir = Path(temp_dir)
        _copy_data_dir(source, isolated_data_dir)
        energy_service = EnergyOptimizationService(EnergyJsonRepository(isolated_data_dir))
        results = [
            _evaluate_instruction_contract(),
            _evaluate_track2_mandates(),
            _evaluate_energy_simulation(energy_service),
            _evaluate_energy_business_impact(energy_service),
        ]
    passed = sum(1 for result in results if result.passed)
    return EvaluationReport(
        total=len(results),
        passed=passed,
        failed=len(results) - passed,
        results=results,
    )


def write_report(path: Path, report: EvaluationReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
