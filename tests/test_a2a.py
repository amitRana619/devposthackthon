import json
from pathlib import Path

from starlette.testclient import TestClient


def test_a2a_agent_card_declares_b2b_skills_and_adk_extension() -> None:
    card = json.loads(Path("a2a/agent-card.json").read_text(encoding="utf-8"))

    assert card["name"] == "energy_ops_agent"
    assert "B2B" in card["description"]
    assert {skill["id"] for skill in card["skills"]} == {
        "extreme_weather_energy_optimization",
        "energy_simulation_observability",
    }
    assert card["capabilities"]["extensions"][0]["uri"].endswith("/a2a-extension/")


def test_adk_agent_declares_multi_agent_orchestration() -> None:
    from startup_ops_agent.agent import root_agent

    assert [agent.name for agent in root_agent.sub_agents] == [
        "weather_pricing_grounding_agent",
        "comfort_cost_conflict_agent",
        "energy_action_governance_agent",
    ]


def test_a2a_runtime_serves_well_known_agent_card() -> None:
    from startup_ops_agent.a2a_app import a2a_app

    with TestClient(a2a_app) as client:
        response = client.get("/.well-known/agent-card.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "energy_ops_agent"
    assert payload["skills"][0]["id"] == "extreme_weather_energy_optimization"
