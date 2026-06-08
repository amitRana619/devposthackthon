"""Deployment skeleton for Gemini Enterprise Agent Platform / Agent Engine.

This file documents the intended Agent Engine deployment shape. It is kept
separate from normal tests because it requires a configured Google Cloud project,
credentials, enabled APIs, and cloud-side permissions.
"""

from __future__ import annotations

import os


def main() -> None:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "PROJECT_ID")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    staging_bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET", "gs://YOUR_STAGING_BUCKET")

    print(
        "Deploy with the Google Cloud Agent Engine SDK using:",
        {
            "project": project_id,
            "location": location,
            "staging_bucket": staging_bucket,
            "agent_module": "startup_ops_agent.agent",
            "agent_object": "root_agent",
            "a2a_entrypoint": "startup_ops_agent.a2a_app:a2a_app",
        },
    )
    print(
        "Install cloud deployment extras first: "
        "python -m pip install -e '.[cloud]'"
    )


if __name__ == "__main__":
    main()
