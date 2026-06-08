from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from startup_ops_agent.models import Account, Interaction, Opportunity, SupportTicket, Task

ModelT = TypeVar("ModelT", bound=BaseModel)


class DataAccessError(RuntimeError):
    pass


class JsonRepository:
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

    def accounts(self) -> list[Account]:
        return self._load_list("accounts.json", Account)

    def opportunities(self) -> list[Opportunity]:
        return self._load_list("opportunities.json", Opportunity)

    def interactions(self) -> list[Interaction]:
        return self._load_list("interactions.json", Interaction)

    def support_tickets(self) -> list[SupportTicket]:
        return self._load_list("support_tickets.json", SupportTicket)

    def tasks(self) -> list[Task]:
        return self._load_list("tasks.json", Task)

    def save_tasks(self, tasks: Iterable[Task]) -> None:
        path = self._resolve("tasks.json")
        serialized = [
            json.loads(task.model_dump_json())
            for task in sorted(tasks, key=lambda task: task.created_at.isoformat())
        ]
        temp_path = path.with_suffix(".json.tmp")
        temp_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
        temp_path.replace(path)

    def append_audit_event(self, event: dict[str, object]) -> None:
        path = self._resolve("audit_log.jsonl")
        payload = {
            "recorded_at": datetime.now(UTC).isoformat(),
            **event,
        }
        with path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(payload, sort_keys=True) + "\n")

