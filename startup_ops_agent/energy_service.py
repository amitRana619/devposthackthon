from __future__ import annotations

import hashlib

from startup_ops_agent.energy_models import (
    BuildingProfile,
    EnergyAction,
    EnergyOptimizationPlan,
    EnergyPriority,
    FlexibleLoad,
    LoadShedDecision,
    OccupancyProfile,
    SimulationResult,
    TraceStep,
    UtilityPricingEvent,
    WeatherEvent,
)
from startup_ops_agent.energy_repository import EnergyJsonRepository
from startup_ops_agent.service import NotFoundError


def _stable_id(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


class EnergyOptimizationService:
    def __init__(self, repository: EnergyJsonRepository) -> None:
        self.repository = repository

    def build_optimization_plan(
        self,
        *,
        building_id: str,
        weather_event_id: str,
        pricing_event_id: str,
        occupancy_id: str,
    ) -> EnergyOptimizationPlan:
        building = self._building(building_id)
        weather = self._weather(weather_event_id)
        pricing = self._pricing(pricing_event_id)
        occupancy = self._occupancy(occupancy_id)
        if occupancy.building_id != building.building_id:
            raise NotFoundError("Occupancy profile does not belong to the requested building.")

        extreme_weather = weather.severity == "extreme" or weather.heat_risk_level >= 3
        peak_pricing = pricing.price_multiplier >= 2.0 or pricing.demand_response_requested_kw > 0
        vulnerable_or_critical = occupancy.vulnerable_occupants or bool(
            set(occupancy.occupied_zones).intersection(building.critical_zones)
        )
        conflicts: list[str] = []
        if extreme_weather and peak_pricing:
            conflicts.append("extreme_weather_peak_pricing")

        if extreme_weather and vulnerable_or_critical:
            primary = EnergyPriority.safety
            setpoint = building.normal_setpoint_c
            decision = "Preserve safety-critical comfort and shed only flexible/non-critical load."
        elif extreme_weather:
            primary = EnergyPriority.comfort
            setpoint = min(building.max_safe_setpoint_c, building.normal_setpoint_c + 1.0)
            decision = "Bias toward occupant comfort while allowing a narrow setpoint adjustment."
        elif peak_pricing:
            primary = EnergyPriority.cost
            setpoint = min(building.max_safe_setpoint_c, building.normal_setpoint_c + 2.0)
            decision = (
                "Prioritize cost reduction because comfort and safety constraints are normal."
            )
        else:
            primary = EnergyPriority.resilience
            setpoint = building.normal_setpoint_c
            decision = "Maintain normal operations and monitor grid and weather changes."

        load_shed = self._load_shed_decisions(
            building=building,
            pricing=pricing,
            primary=primary,
            vulnerable_or_critical=vulnerable_or_critical,
        )
        shed_kw = round(sum(decision.shed_kw for decision in load_shed), 2)
        source_ids = [
            building.building_id,
            weather.event_id,
            pricing.pricing_event_id,
            occupancy.occupancy_id,
        ]
        return EnergyOptimizationPlan(
            plan_id=f"energy-plan-{_stable_id(*source_ids)}",
            building_id=building.building_id,
            decision=decision,
            primary_priority=primary,
            setpoint_c=setpoint,
            expected_load_shed_kw=shed_kw,
            load_shed=load_shed,
            estimated_cost_avoidance_usd=self._estimated_cost_avoidance(shed_kw, pricing),
            estimated_business_risk_avoided_usd=self._business_risk_avoided(
                building=building,
                primary=primary,
                vulnerable_or_critical=vulnerable_or_critical,
            ),
            actions=self._actions(building, weather, pricing, primary, source_ids),
            conflicts=conflicts,
            compliance_notes=self._compliance_notes(building, weather, vulnerable_or_critical),
            real_world_basis=self._real_world_basis(weather, pricing),
            source_ids=source_ids,
        )

    def run_simulation_case(self, case_id: str) -> SimulationResult:
        case = self._case(case_id)
        trace = [
            TraceStep(
                step="retrieve_context",
                decision="Loaded building, weather, pricing, and occupancy records.",
                reason="Track 2 simulation requires multi-variable rare-event context.",
                source_ids=[
                    case.building_id,
                    case.weather_event_id,
                    case.pricing_event_id,
                    case.occupancy_id,
                ],
            )
        ]
        plan = self.build_optimization_plan(
            building_id=case.building_id,
            weather_event_id=case.weather_event_id,
            pricing_event_id=case.pricing_event_id,
            occupancy_id=case.occupancy_id,
        )
        trace.append(
            TraceStep(
                step="resolve_conflict",
                decision=plan.primary_priority.value,
                reason=plan.decision,
                source_ids=plan.source_ids,
            )
        )
        passed = (
            plan.primary_priority == case.expected_primary_priority
            and bool(plan.conflicts) == case.expected_conflict
        )
        return SimulationResult(
            case_id=case.case_id,
            passed=passed,
            plan=plan,
            trace=trace,
            failure_reason=None
            if passed
            else "Plan priority or conflict detection did not match expected simulation outcome.",
        )

    def run_all_simulations(self) -> list[SimulationResult]:
        return [
            self.run_simulation_case(case.case_id)
            for case in self.repository.simulation_cases()
        ]

    def _load_by_id(self, items: list, field: str, value: str):
        for item in items:
            if getattr(item, field) == value:
                return item
        raise NotFoundError(f"Energy record not found: {value}")

    def _building(self, building_id: str) -> BuildingProfile:
        return self._load_by_id(self.repository.buildings(), "building_id", building_id)

    def _weather(self, event_id: str) -> WeatherEvent:
        return self._load_by_id(self.repository.weather_events(), "event_id", event_id)

    def _pricing(self, pricing_event_id: str) -> UtilityPricingEvent:
        return self._load_by_id(
            self.repository.pricing_events(),
            "pricing_event_id",
            pricing_event_id,
        )

    def _occupancy(self, occupancy_id: str) -> OccupancyProfile:
        return self._load_by_id(self.repository.occupancy_profiles(), "occupancy_id", occupancy_id)

    def _case(self, case_id: str):
        return self._load_by_id(self.repository.simulation_cases(), "case_id", case_id)

    def _load_shed_decisions(
        self,
        *,
        building: BuildingProfile,
        pricing: UtilityPricingEvent,
        primary: EnergyPriority,
        vulnerable_or_critical: bool,
    ) -> list[LoadShedDecision]:
        eligible_loads = self._eligible_flexible_loads(
            building=building,
            vulnerable_or_critical=vulnerable_or_critical,
        )
        flexible_capacity = sum(load.max_shed_kw for load in eligible_loads)
        if primary == EnergyPriority.safety and vulnerable_or_critical:
            target_kw = pricing.demand_response_requested_kw * 0.45
        elif primary == EnergyPriority.cost:
            target_kw = max(pricing.demand_response_requested_kw, 24.0)
        else:
            target_kw = pricing.demand_response_requested_kw * 0.7

        return self._allocate_load_shed(
            eligible_loads=eligible_loads,
            target_kw=min(flexible_capacity, target_kw),
            primary=primary,
        )

    def _eligible_flexible_loads(
        self,
        *,
        building: BuildingProfile,
        vulnerable_or_critical: bool,
    ) -> list[FlexibleLoad]:
        if not vulnerable_or_critical:
            return building.flexible_loads

        critical_zones = set(building.critical_zones)
        return [
            load
            for load in building.flexible_loads
            if not critical_zones.intersection(load.zones)
        ]

    def _allocate_load_shed(
        self,
        *,
        eligible_loads: list[FlexibleLoad],
        target_kw: float,
        primary: EnergyPriority,
    ) -> list[LoadShedDecision]:
        remaining_kw = round(target_kw, 2)
        decisions: list[LoadShedDecision] = []
        for load in sorted(eligible_loads, key=lambda item: item.load_id):
            if remaining_kw <= 0:
                break
            shed_kw = round(min(load.max_shed_kw, remaining_kw), 2)
            if shed_kw <= 0:
                continue
            remaining_kw = round(remaining_kw - shed_kw, 2)
            decisions.append(
                LoadShedDecision(
                    load_id=load.load_id,
                    shed_kw=shed_kw,
                    reason=(
                        "Selected as a controllable non-critical load before changing "
                        "critical-zone HVAC."
                        if primary == EnergyPriority.safety
                        else "Selected to meet utility demand-response target."
                    ),
                )
            )
        return decisions

    def _estimated_cost_avoidance(
        self,
        shed_kw: float,
        pricing: UtilityPricingEvent,
    ) -> float:
        return round(shed_kw * pricing.demand_charge_usd_per_kw * pricing.price_multiplier, 2)

    def _business_risk_avoided(
        self,
        *,
        building: BuildingProfile,
        primary: EnergyPriority,
        vulnerable_or_critical: bool,
    ) -> float:
        if primary != EnergyPriority.safety or not vulnerable_or_critical:
            return 0.0
        return round(
            building.business_value_at_risk_usd_per_hour
            * building.business_risk_protection_factor,
            2,
        )

    def _compliance_notes(
        self,
        building: BuildingProfile,
        weather: WeatherEvent,
        vulnerable_or_critical: bool,
    ) -> list[str]:
        notes = [
            "Do not relax HVAC controls for critical zones before exhausting flexible loads.",
            f"Critical-zone policy: {building.critical_zone_policy}",
        ]
        if weather.heat_risk_level >= 3 or vulnerable_or_critical:
            notes.append(
                "Heat-risk workflow requires occupant safety review before cost optimization."
            )
        return notes

    def _real_world_basis(
        self,
        weather: WeatherEvent,
        pricing: UtilityPricingEvent,
    ) -> list[str]:
        basis = [
            (
                "DOE/NREL grid-interactive efficient buildings: use demand "
                "flexibility from controllable building loads."
            ),
            (
                "OSHA/NIOSH heat stress guidance: workplace heat hazards "
                "require controls that reduce heat exposure."
            ),
        ]
        if weather.heat_risk_level >= 3:
            basis.append(
                "NOAA/NWS HeatRisk: high and extreme heat levels indicate "
                "elevated heat-health risk."
            )
        if pricing.demand_response_requested_kw > 0:
            basis.append(
                "Utility demand response: reduce load during peak events "
                "without violating safety constraints."
            )
        return basis

    def _actions(
        self,
        building: BuildingProfile,
        weather: WeatherEvent,
        pricing: UtilityPricingEvent,
        primary: EnergyPriority,
        source_ids: list[str],
    ) -> list[EnergyAction]:
        actions = [
            EnergyAction(
                action_id=f"action-{_stable_id('setpoint', *source_ids)}",
                title="Set HVAC policy for occupied and critical zones",
                priority=primary,
                explanation=(
                    "Resolve comfort versus cost using explicit safety-first priority rules."
                ),
                source_ids=source_ids,
            )
        ]
        if pricing.demand_response_requested_kw > 0:
            actions.append(
                EnergyAction(
                    action_id=f"action-{_stable_id('shed', *source_ids)}",
                    title="Shed flexible loads without touching critical zones",
                    priority=EnergyPriority.cost
                    if primary != EnergyPriority.safety
                    else EnergyPriority.safety,
                    explanation=(
                        "Use flexible loads for demand response; "
                        "critical HVAC zones remain protected."
                    ),
                    source_ids=[building.building_id, pricing.pricing_event_id],
                )
            )
        if weather.severity in {"high", "extreme"}:
            actions.append(
                EnergyAction(
                    action_id=f"action-{_stable_id('monitor', *source_ids)}",
                    title="Increase weather and grid monitoring cadence",
                    priority=EnergyPriority.resilience,
                    explanation=(
                        "Rare weather events can change grid and comfort constraints quickly."
                    ),
                    source_ids=[weather.event_id],
                )
            )
        return actions
