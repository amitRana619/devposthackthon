# Google Cloud Deployment

## Local Container

```powershell
docker build -t energy-ops-agent:0.1.0 .
docker run --rm -p 8080:8080 energy-ops-agent:0.1.0
```

The container serves the A2A runtime. Check the well-known agent card:

```powershell
Invoke-WebRequest http://localhost:8080/.well-known/agent-card.json -UseBasicParsing
```

## Cloud Run Shape

`cloudrun-service.yaml` defines:

- Cloud Run service
- port `8080`
- startup and liveness probes against the A2A agent card
- dedicated service account placeholder
- model and actor environment variables

Before deploying, replace:

- `PROJECT_ID`
- Artifact Registry image path
- service account name
- secret bindings

## Recommended Google Cloud Services

- Gemini Enterprise Agent Platform / Agent Engine for managed agent runtime
- Cloud Run for the API container
- Artifact Registry for container images
- Secret Manager for Gemini and connector credentials
- Cloud Logging for audit and operational logs
- Cloud Trace for request/tool latency
- Firestore or Cloud SQL for durable plans, simulation traces, and audit state

## Agent Engine Preparation

`agent-engine-deploy.py` records the expected Agent Engine deployment metadata.
It intentionally does not run in normal tests because actual deployment requires
Google Cloud credentials, an enabled project, staging bucket, and permissions.

Install cloud deployment tooling with:

```powershell
python -m pip install -e ".[cloud]"
```
