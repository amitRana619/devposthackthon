from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from startup_ops_agent.config import default_data_dir
from startup_ops_agent.models import ActionType
from startup_ops_agent.policy import PermissionDeniedError, parse_actor
from startup_ops_agent.repository import JsonRepository
from startup_ops_agent.service import StartupOpsService


@pytest.fixture()
def data_dir(tmp_path: Path) -> Path:
    source = default_data_dir()
    for path in source.iterdir():
        if path.is_file():
            shutil.copy(path, tmp_path / path.name)
    return tmp_path


def test_account_brief_scores_customer_and_pipeline_risks(data_dir: Path) -> None:
    service = StartupOpsService(JsonRepository(data_dir))
    actor = parse_actor("founder-001", "founder")

    brief = service.build_account_brief(
        account_id="acme-robotics",
        actor=actor,
        today=date(2026, 6, 1),
    )

    categories = {risk.category for risk in brief.risk_signals}
    assert categories == {"pipeline", "relationship", "renewal", "support"}
    assert brief.risk_signals[0].level == "high"
    assert any(action.action_type == ActionType.draft_email for action in brief.recommended_actions)


def test_create_task_draft_is_idempotent(data_dir: Path) -> None:
    service = StartupOpsService(JsonRepository(data_dir))
    actor = parse_actor("founder-001", "founder")

    first = service.create_task_draft(
        account_id="acme-robotics",
        actor=actor,
        title="Escalate unresolved customer support risk",
        action_type=ActionType.create_task,
        source_ids=["sup-acme-sso"],
    )
    second = service.create_task_draft(
        account_id="acme-robotics",
        actor=actor,
        title="Escalate unresolved customer support risk",
        action_type=ActionType.create_task,
        source_ids=["sup-acme-sso"],
    )

    assert first.task_id == second.task_id
    saved_tasks = json.loads((data_dir / "tasks.json").read_text(encoding="utf-8"))
    assert len(saved_tasks) == 1


def test_viewer_cannot_create_task_draft(data_dir: Path) -> None:
    service = StartupOpsService(JsonRepository(data_dir))
    actor = parse_actor("viewer-001", "viewer")

    with pytest.raises(PermissionDeniedError):
        service.create_task_draft(
            account_id="acme-robotics",
            actor=actor,
            title="Escalate unresolved customer support risk",
            action_type=ActionType.create_task,
            source_ids=["sup-acme-sso"],
        )

