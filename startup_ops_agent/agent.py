from __future__ import annotations

import sys

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from startup_ops_agent.config import load_settings
from startup_ops_agent.instructions import build_agent_instruction

load_dotenv()
settings = load_settings()

grounding_agent = Agent(
    model=settings.model,
    name="weather_pricing_grounding_agent",
    description=(
        "Retrieves building, weather, utility pricing, occupancy, and policy context "
        "from MCP-backed operating systems."
    ),
    instruction=(
        "Use MCP tools to gather source-backed energy operations context. Preserve "
        "source IDs exactly. Do not summarize unsupported facts."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "startup_ops_agent.mcp_server"],
                )
            )
        )
    ],
)

risk_analysis_agent = Agent(
    model=settings.model,
    name="comfort_cost_conflict_agent",
    description=(
        "Analyzes grounded building context for occupant comfort, safety, and "
        "peak-demand cost conflicts."
    ),
    instruction=(
        "Analyze only grounded context from weather_pricing_grounding_agent. During "
        "extreme weather, occupant safety outranks cost. Explain the conflict with "
        "source IDs."
    ),
)

action_governance_agent = Agent(
    model=settings.model,
    name="energy_action_governance_agent",
    description=(
        "Turns energy recommendations into safe HVAC and load-shedding actions while "
        "preserving comfort, critical-zone, and observability boundaries."
    ),
    instruction=(
        "Before recommending actions, verify critical zones and occupant vulnerability. "
        "Shed flexible loads before changing critical-zone comfort."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "startup_ops_agent.mcp_server"],
                )
            )
        )
    ],
)

root_agent = Agent(
    model=settings.model,
    name="energy_ops_agent",
    description=(
        "Optimized B2B building energy agent that resolves extreme weather and "
        "peak-demand utility pricing conflicts."
    ),
    instruction=build_agent_instruction(settings),
    sub_agents=[grounding_agent, risk_analysis_agent, action_governance_agent],
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "startup_ops_agent.mcp_server"],
                )
            )
        )
    ],
)
