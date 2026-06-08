# Google Cloud Marketplace Readiness

This folder contains Marketplace-style preparation notes. The selected challenge
track is Track 2, so these artifacts are supporting deployment collateral rather
than the primary submission package. It does not
claim the product is already approved by Google Cloud Marketplace; it provides
the technical and operational evidence needed for review preparation.

## Runtime Shape

- Container image exposes `startup_ops_agent.api:app` on port `8080`.
- `/healthz` supports Cloud Run health checks.
- `/v1/enterprise-manifest` exposes product metadata for reviewers and
  enterprise integration smoke tests.
- `/v1/energy-plan` exposes deterministic B2B energy optimization behavior for demos
  and integration testing.
- `/v1/evaluations` exposes the enterprise readiness gate.

## Security Requirements

- Put real API keys in Secret Manager, not source code.
- Run with a dedicated service account.
- Scope external BMS, weather, utility tariff, and occupancy adapters by tenant
  and building.
- Keep action execution approval-gated unless the buyer explicitly configures
  production write permissions.

## Buyer Configuration

Required:

- Gemini API or Vertex AI model access.
- Data adapter credentials for BMS, weather, utility tariff, and occupancy systems.

Optional:

- Cloud Logging sink.
- Cloud Trace exporter.
- Firestore or Cloud SQL for durable plans, simulation traces, and audit state.
