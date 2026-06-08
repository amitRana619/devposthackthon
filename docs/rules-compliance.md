# Rules And Mandates Compliance

Source reviewed: `C:\Users\mbpd1\Downloads\Google for Startups AI Agents Challenge Rules.pdf`.

## Selected Track

Track 2: Optimize (Existing Agents).

The rules state that submissions must select one challenge track. This repository
is now documented and packaged for Track 2 only.

## Track 2 Mandates

| Mandate | Implementation Evidence |
| --- | --- |
| Existing Agent Optimized | The original ADK multi-agent shell remains, but the default readiness path now targets B2B building-energy operations. |
| Real-World Edge Case | `sample_data/energy_simulation_cases.json` includes the heat-dome plus peak-demand surge scenario. |
| Agent Simulation | `python -m startup_ops_agent.cli simulate-energy` runs synthetic multi-variable cases. |
| Agent Observability | `SimulationResult.trace` records context retrieval and conflict resolution steps. |
| Agent Optimizer | `startup_ops_agent/optimizer.py` adds missing rare-event safety clauses. |
| B2B Focus | The energy plan reports load-level demand response, cost avoidance, and protected business risk. |
| Google Cloud Powered Intelligence | `startup_ops_agent/agent.py` configures Gemini-backed ADK agents. |
| A2A Interoperability | `startup_ops_agent/a2a_app.py` exposes the ADK root agent via A2A; `a2a/agent-card.json` documents discovery metadata. |
| ADK Orchestration | Root ADK agent coordinates weather/pricing grounding, comfort-cost conflict analysis, and action governance sub-agents. |
| Grounding/RAG | MCP tools retrieve building, weather, utility pricing, and occupancy data before recommendations. |

## Submission Requirements From Rules

| Requirement | Status |
| --- | --- |
| Project built with required tools | Implemented with ADK, Gemini model config, MCP, A2A, Cloud Run/Agent Engine packaging. |
| One selected track | Track 2 only. |
| Text description | `docs/submission.md`, `README.md`. |
| Architecture diagram | `docs/architecture.md`. |
| Code repository URL | Must be provided on Devpost after pushing to a public or judge-accessible repository. |
| 1-2 minute demo video | Script exists in `docs/demo-script.md`; video still needs recording. |
| Testing access | Local commands exist; public deployed URL still must be supplied after Cloud Run or Agent Engine deployment. |
| English language | Docs and UI/demo copy are in English. |

## Remaining External Submission Steps

These cannot be completed purely in the local repository:

1. Deploy the A2A runtime to Google Cloud.
2. Provide the deployed URL and any login/test instructions.
3. Push the code to the repository URL used for judging.
4. Record and upload the 1-2 minute demo video.
