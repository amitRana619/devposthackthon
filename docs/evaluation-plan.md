# Track 2 Evaluation Plan

## Success Criteria

- The agent retrieves grounded building, weather, pricing, and occupancy data.
- Extreme weather plus peak-demand surge is detected as a conflict.
- Critical occupancy makes safety outrank energy cost.
- Flexible-load capacity comes from building data, not fixed prompt assumptions.
- Non-critical loads are selected before critical-zone comfort is changed.
- Cost avoidance and protected business risk are returned from deterministic fields.
- Every simulation emits observability trace steps.
- Instruction optimizer detects and adds missing conflict-handling rules.

## Automated Tests

The current test suite covers:

- rare-event simulation
- safety-versus-cost priority
- observability trace shape
- load-level demand-response allocation
- B2B cost and business-risk impact fields
- instruction optimizer behavior
- legacy account-risk tests remain in the test suite as regression coverage, but
  the default readiness evaluation is Track 2 energy-focused

Run:

```powershell
pytest
python -m startup_ops_agent.cli evaluate --output reports/evaluation.json
```
