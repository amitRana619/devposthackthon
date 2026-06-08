from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ActorRole(StrEnum):
    founder = "founder"
    operator = "operator"
    viewer = "viewer"


class ActionType(StrEnum):
    create_task = "create_task"
    draft_email = "draft_email"
    update_stage = "update_stage"


class RiskLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class Account(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    name: str
    owner_id: str
    health_score: int = Field(ge=0, le=100)
    arr_usd: int = Field(ge=0)
    renewal_date: date
    region: str
    plan: str


class Opportunity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_id: str
    account_id: str
    name: str
    stage: str
    amount_usd: int = Field(ge=0)
    close_date: date
    last_activity_date: date


class Interaction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interaction_id: str
    account_id: str
    occurred_at: datetime
    channel: str
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str


class SupportTicket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: str
    account_id: str
    severity: Literal["low", "medium", "high", "critical"]
    status: Literal["open", "pending_customer", "resolved"]
    opened_at: datetime
    title: str


class Task(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    account_id: str
    action_type: ActionType
    title: str
    owner_id: str
    status: Literal["draft", "approved", "done", "cancelled"] = "draft"
    created_at: datetime
    idempotency_key: str
    source_ids: list[str] = Field(default_factory=list)


class RiskSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_id: str
    level: RiskLevel
    category: str
    summary: str
    source_ids: list[str]


class RecommendedAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: ActionType
    title: str
    reason: str
    requires_approval: bool
    source_ids: list[str]


class AccountBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account: Account
    opportunities: list[Opportunity]
    interactions: list[Interaction]
    support_tickets: list[SupportTicket]
    open_tasks: list[Task]
    risk_signals: list[RiskSignal]
    recommended_actions: list[RecommendedAction]

