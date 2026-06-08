from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    actor_id: str
    actor_role: str
    model: str


def default_data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "sample_data"


def load_settings() -> Settings:
    data_dir = Path(os.getenv("STARTUP_OPS_DATA_DIR", str(default_data_dir()))).resolve()
    return Settings(
        data_dir=data_dir,
        actor_id=os.getenv("STARTUP_OPS_ACTOR_ID", "founder-001"),
        actor_role=os.getenv("STARTUP_OPS_ACTOR_ROLE", "founder"),
        model=os.getenv("STARTUP_OPS_MODEL", "gemini-flash-latest"),
    )

