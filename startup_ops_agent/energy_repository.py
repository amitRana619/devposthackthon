from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from startup_ops_agent.energy_models import (
    BuildingProfile,
    OccupancyProfile,
    SimulationCase,
    UtilityPricingEvent,
    WeatherEvent,
)
from startup_ops_agent.repository import DataAccessError

ModelT = TypeVar("ModelT", bound=BaseModel)


class EnergyJsonRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir.resolve()

    def _resolve(self, filename: str) -> Path:
        path = (self.data_dir / filename).resolve()
        if self.data_dir not in path.parents and path != self.data_dir:
            raise DataAccessError("Resolved path escaped the configured data directory.")
        return path

    def _load_list(self, filename: str, model: type[ModelT]) -> list[ModelT]:
        path = self._resolve(filename)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise DataAccessError(f"Required data file is missing: {filename}") from exc
        except json.JSONDecodeError as exc:
            raise DataAccessError(f"Data file is not valid JSON: {filename}") from exc
        if not isinstance(raw, list):
            raise DataAccessError(f"Data file must contain a JSON list: {filename}")
        return [model.model_validate(item) for item in raw]

    def buildings(self) -> list[BuildingProfile]:
        return self._load_list("energy_buildings.json", BuildingProfile)

    def weather_events(self) -> list[WeatherEvent]:
        return self._load_list("energy_weather_events.json", WeatherEvent)

    def pricing_events(self) -> list[UtilityPricingEvent]:
        return self._load_list("energy_pricing_events.json", UtilityPricingEvent)

    def occupancy_profiles(self) -> list[OccupancyProfile]:
        return self._load_list("energy_occupancy.json", OccupancyProfile)

    def simulation_cases(self) -> list[SimulationCase]:
        return self._load_list("energy_simulation_cases.json", SimulationCase)

