# Track 2 Readiness Note

This repository is currently focused on **Track 2: Optimize (Existing Agents)**,
not Track 3. This file remains only to avoid stale links from earlier drafts.

## Current Readiness Evidence

- `startup_ops_agent/agent.py` defines a Gemini-backed ADK root agent with
  weather/pricing grounding, comfort-cost conflict, and energy action governance
  sub-agents.
- `startup_ops_agent/energy_service.py` owns deterministic safety-versus-cost
  conflict resolution.
- `sample_data/energy_simulation_cases.json` contains synthetic normal-day and
  rare-event cases.
- `startup_ops_agent/evaluation.py` now runs Track 2-focused readiness checks.
- `a2a/agent-card.json` exposes enterprise agent discovery metadata.
- `Dockerfile` and `deploy/cloudrun-service.yaml` keep the runtime Cloud Run
  deployable.

## Readiness Gate

Run:

```powershell
python -m startup_ops_agent.cli evaluate --output reports/evaluation.json
```

The gate validates:

- energy instruction contract coverage
- ADK multi-agent structure
- rare extreme-weather plus peak-pricing simulation
- load-level B2B business-impact evidence
