# Demo Script

## Opening

"Energy Ops Agent is an existing ADK multi-agent system optimized for a rare
real-world event: an extreme heat dome happening during a utility peak-demand
pricing surge."

## Scene 1: Existing Agents

Show:

- `startup_ops_agent/agent.py`
- grounding agent
- comfort/cost conflict agent
- action governance agent

## Scene 2: Rare Event Simulation

Command:

```powershell
python -m startup_ops_agent.cli simulate-energy
```

Show:

- normal-day cases pass
- heat-dome plus peak-surge case passes
- trace includes context retrieval and conflict resolution

## Scene 3: Optimized Decision

Command:

```powershell
python -m startup_ops_agent.cli energy-plan --building bldg-medtech-hq --weather weather-heat-dome --pricing pricing-peak-surge --occupancy occupancy-business-critical
```

Show:

- `primary_priority` is `safety`
- critical setpoint remains `23.0`
- only flexible load shedding is recommended
- source IDs are preserved

## Scene 4: Agent Optimizer

Command:

```powershell
python -m startup_ops_agent.cli optimize-energy-instruction --instruction "You are an energy assistant."
```

Show missing conflict clauses added programmatically.

## Close

"The optimized agent now handles the real-world conflict it previously stalled
on: comfort and safety during extreme weather versus cost reduction during peak
pricing."
