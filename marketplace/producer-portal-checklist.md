# Producer Portal Checklist

This is a preparation checklist for a future Google Cloud Marketplace review.

## Organization

- Confirm Google Cloud Partner Network membership.
- Confirm Cloud Marketplace vendor account and payment profile.
- Confirm supported incorporation region.

## Product

- Confirm production-ready status.
- Complete vulnerability scanning for the container image.
- Finalize public product page and support motion.
- Finalize pricing model and entitlement handling.
- Confirm product runs primarily on Google Cloud.

## Technical Package

- Build and scan the container image.
- Push image to Artifact Registry.
- Deploy Cloud Run service with least-privilege service account.
- Configure Secret Manager for Gemini and connector credentials.
- Enable Cloud Logging and Cloud Trace.
- Export OpenAPI schema from FastAPI.
- Run `python -m startup_ops_agent.cli evaluate`.

## Buyer Onboarding

- Document required connector credentials.
- Document sample prompts and API calls.
- Document tenant isolation settings.
- Document support escalation process.

