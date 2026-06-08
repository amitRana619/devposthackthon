from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EnergyPriority(StrEnum):
    safety = "safety"
    comfort = "comfort"
    cost = "cost"
    resilience = "resilience"


class FlexibleLoad(BaseModel):
    model_config = ConfigDict(extra="forbid")

    load_id: str
    description: str
    zones: list[str]
    max_shed_kw: float = Field(ge=0)


class BuildingProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    building_id: str
    name: str
    tenant_id: str
    business_type: str
    hvac_zones: list[str]
    critical_zones: list[str]
    flexible_loads: list[FlexibleLoad]
    normal_setpoint_c: float
    max_safe_setpoint_c: float
    min_safe_setpoint_c: float
    business_value_at_risk_usd_per_hour: float = Field(ge=0)
    business_risk_protection_factor: float = Field(ge=0, le=1)
    critical_zone_policy: str


class WeatherEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    kind: Literal["normal", "heat_wave", "cold_snap", "storm"]
    severity: Literal["low", "medium", "high", "extreme"]
    forecast_start: datetime
    forecast_end: datetime
    outdoor_temp_c: float
    heat_risk_level: int = Field(ge=0, le=4)
    grid_risk: Literal["low", "medium", "high"]
    source: str


class UtilityPricingEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pricing_event_id: str
    provider: str
    starts_at: datetime
    ends_at: datetime
    price_multiplier: float = Field(ge=1.0)
    demand_response_requested_kw: float = Field(ge=0)
    demand_charge_usd_per_kw: float = Field(ge=0)
    source: str


class OccupancyProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    occupancy_id: str
    building_id: str
    occupied_zones: list[str]
    vulnerable_occupants: bool
    business_hours: bool


class EnergyAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str
    title: str
    priority: EnergyPriority
    explanation: str
    source_ids: list[str]


class LoadShedDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    load_id: str
    shed_kw: float = Field(ge=0)
    reason: str


class EnergyOptimizationPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    building_id: str
    decision: str
    primary_priority: EnergyPriority
    setpoint_c: float
    expected_load_shed_kw: float
    load_shed: list[LoadShedDecision]
    estimated_cost_avoidance_usd: float
    estimated_business_risk_avoided_usd: float
    actions: list[EnergyAction]
    conflicts: list[str]
    compliance_notes: list[str]
    real_world_basis: list[str]
    source_ids: list[str]


class SimulationCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    building_id: str
    weather_event_id: str
    pricing_event_id: str
    occupancy_id: str
    expected_primary_priority: EnergyPriority
    expected_conflict: bool


class TraceStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: str
    decision: str
    reason: str
    source_ids: list[str]


class SimulationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    passed: bool
    plan: EnergyOptimizationPlan
    trace: list[TraceStep]
    failure_reason: str | None = None
