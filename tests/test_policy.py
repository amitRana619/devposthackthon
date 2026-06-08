import pytest

from startup_ops_agent.models import ActionType
from startup_ops_agent.policy import PermissionDeniedError, ensure_action_allowed, parse_actor


def test_viewer_cannot_create_task() -> None:
    actor = parse_actor("viewer-1", "viewer")

    with pytest.raises(PermissionDeniedError):
        ensure_action_allowed(actor, ActionType.create_task)


def test_operator_can_draft_email_but_cannot_update_stage() -> None:
    actor = parse_actor("operator-1", "operator")

    ensure_action_allowed(actor, ActionType.draft_email)
    with pytest.raises(PermissionDeniedError):
        ensure_action_allowed(actor, ActionType.update_stage)

