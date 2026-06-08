from __future__ import annotations

import os
from pathlib import Path

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from startup_ops_agent.agent import root_agent

AGENT_CARD_PATH = Path(__file__).resolve().parents[1] / "a2a" / "agent-card.json"

a2a_app = to_a2a(
    root_agent,
    port=int(os.getenv("PORT", "8080")),
    agent_card=str(AGENT_CARD_PATH),
)

