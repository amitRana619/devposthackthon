# Track 2 Optimization

## Existing Agent

The project started as a working ADK multi-agent system with MCP tools,
deterministic business logic, tests, and an A2A runtime. For Track 2, the system
has been optimized for B2B building energy operations.

## Failure Mode

The normal-day agent can reduce energy cost during ordinary peak pricing. It can
also preserve comfort during ordinary weather events. The hard production edge
case is when both occur at once:

- extreme heat dome
- utility peak-demand surge
- critical building zones occupied
- vulnerable occupants present

Without explicit optimization, the agent can stall between two competing goals:

- reduce cost by relaxing HVAC and shedding load
- preserve occupant safety and critical-zone comfort

## Agent Simulation

Synthetic cases live in `sample_data/energy_simulation_cases.json`.

Run:

```powershell
python -m startup_ops_agent.cli simulate-energy
```

Current cases:

- normal day, standard price
- normal day, peak-demand price
- heat dome, peak-demand price, critical occupancy

## Agent Observability

Each simulation emits trace steps:

- `retrieve_context`
- `resolve_conflict`

The trace records the selected priority, reason, and source IDs used.

## Agent Optimizer

The optimizer in `startup_ops_agent/optimizer.py` checks whether the system
instruction contains the conflict-handling clauses needed for the rare event:

- simulate rare combinations of extreme weather and peak-demand pricing
- occupant safety outranks energy cost during extreme weather
- shed flexible loads before changing critical-zone comfort
- emit an observability trace for every conflict decision

## Optimized Decision Rule

When extreme weather and peak-demand pricing happen at the same time:

1. If critical zones or vulnerable occupants are present, choose `safety`.
2. Keep critical-zone setpoints at the normal safe value.
3. Shed only flexible/non-critical loads.
4. Increase monitoring cadence.
5. Preserve source IDs and trace the decision.

## Real-World B2B Grounding

The optimized planner now includes B2B-operational details that facilities and
energy teams expect:

- estimated demand-response cost avoidance
- estimated business risk avoided for critical-zone protection
- load-level shedding decisions from building data
- HeatRisk-style heat severity levels
- compliance notes for critical-zone HVAC constraints
- real-world basis statements tied to demand flexibility, workplace heat stress,
  and heat-health risk

The service intentionally keeps these calculations deterministic. Gemini can
explain the plan, but it does not invent the financial impact or decide whether
critical zones can be relaxed.

## Latest Optimization Pass

The planner no longer assumes every flexible load has the same capacity. The
building profile now carries each controllable load, its affected zones, and its
maximum shed capacity. During an extreme-weather conflict with critical
occupancy, the service filters out any flexible load tied to critical zones,
allocates only the needed non-critical shed, and returns the selected loads in
the plan.

The readiness evaluation now focuses on Track 2 energy quality gates:

- instruction contract for energy tools and safety clauses
- ADK multi-agent structure
- rare-event simulation pass/fail
- B2B business-impact evidence from load-level shedding, cost avoidance, and
  protected risk
