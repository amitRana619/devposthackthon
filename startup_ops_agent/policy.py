from __future__ import annotations

from dataclasses import dataclass

from startup_ops_agent.models import ActionType, ActorRole


class PermissionDeniedError(RuntimeError):
    pass


ROLE_CAPABILITIES: dict[ActorRole, frozenset[ActionType]] = {
    ActorRole.founder: frozenset(
        {ActionType.create_task, ActionType.draft_email, ActionType.update_stage}
    ),
    ActorRole.operator: frozenset({ActionType.create_task, ActionType.draft_email}),
    ActorRole.viewer: frozenset(),
}

APPROVAL_REQUIRED_ACTIONS: frozenset[ActionType] = frozenset(
    {ActionType.draft_email, ActionType.update_stage}
)


@dataclass(frozen=True)
class Actor:
    actor_id: str
    role: ActorRole


def parse_actor(actor_id: str, role: str) -> Actor:
    try:
        actor_role = ActorRole(role)
    except ValueError as exc:
        raise PermissionDeniedError(f"Unsupported actor role: {role}") from exc
    if not actor_id.strip():
        raise PermissionDeniedError("Actor id is required.")
    return Actor(actor_id=actor_id, role=actor_role)


def ensure_action_allowed(actor: Actor, action_type: ActionType) -> None:
    if action_type not in ROLE_CAPABILITIES[actor.role]:
        raise PermissionDeniedError(
            f"Role '{actor.role.value}' cannot perform '{action_type.value}'."
        )


def requires_approval(action_type: ActionType) -> bool:
    return action_type in APPROVAL_REQUIRED_ACTIONS

