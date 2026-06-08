# Energy Ops Agent

Track: **Optimize (Existing Agents)**

Energy Ops Agent is an optimized ADK multi-agent system for B2B building energy
operations. The existing agent system has been refactored and stress-tested for
rare real-world conflicts: an extreme weather event happening at the same time a
utility provider issues peak-demand surge pricing.

The optimized system uses:

- ADK root agent plus specialist sub-agents
- MCP tools for grounded building, weather, pricing, and occupancy context
- deterministic conflict-resolution service for safety-critical decisions
- synthetic Agent Simulation cases for rare multi-variable events
- observability trace steps for conflict decisions
- instruction optimizer checks for stalled comfort-versus-cost logic
- building-specific controllable-load capacity and B2B financial impact fields
- A2A runtime wrapper for enterprise agent interoperability

## Existing Agents

The current agents live in `startup_ops_agent/agent.py`:

- `energy_ops_agent`: root orchestrator
- `weather_pricing_grounding_agent`: retrieves grounded weather, pricing,
  occupancy, and building context
- `comfort_cost_conflict_agent`: reasons over comfort, safety, and energy cost
  conflicts
- `energy_action_governance_agent`: recommends safe HVAC and flexible-load
  actions without violating critical-zone constraints

## Track 2 Scenario

The hard case is:

```text
Extreme heat dome + peak-demand utility surge + critical building occupancy
```

The optimized behavior is:

1. Detect the conflict between occupant safety and energy cost.
2. Prioritize safety and critical-zone comfort.
3. Shed flexible loads before changing critical-zone HVAC.
4. Return the named non-critical loads selected for demand response.
5. Preserve source IDs from weather, pricing, building, and occupancy records.
6. Emit a trace showing context retrieval and conflict resolution.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Set your Gemini key in `startup_ops_agent/.env`:

```text
GOOGLE_API_KEY="your-key"
```

Do not commit real keys.

## Run The Optimized Energy Plan

```powershell
python -m startup_ops_agent.cli energy-plan `
  --building bldg-medtech-hq `
  --weather weather-heat-dome `
  --pricing pricing-peak-surge `
  --occupancy occupancy-business-critical
```

## Run Agent Simulation

```powershell
python -m startup_ops_agent.cli simulate-energy
```

## Run Readiness Evaluation

```powershell
python -m startup_ops_agent.cli evaluate --output reports/evaluation.json
```

The readiness evaluation is Track 2-focused: instruction contract, multi-agent
structure, rare-event simulation, and B2B business-impact evidence.

## Run With ADK

```powershell
adk web startup_ops_agent --port 8000 --no-reload
```

Try:

```text
Optimize MedTech HQ during the heat dome and peak-demand surge. Prioritize
critical occupants and explain the observability trace.
```

## A2A Runtime

```powershell
uvicorn startup_ops_agent.a2a_app:a2a_app --host 127.0.0.1 --port 8081
```

Agent card:

```text
http://localhost:8081/.well-known/agent-card.json
```

## Test

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
pytest
ruff check .
```

## Submission Assets

- [Architecture](docs/architecture.md)
- [Track 2 optimization plan](docs/track2-optimization.md)
- [Evaluation plan](docs/evaluation-plan.md)
- [Demo script](docs/demo-script.md)
