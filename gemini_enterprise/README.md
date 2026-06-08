# Gemini Enterprise Preparation

This folder prepares the agent for Gemini Enterprise positioning. Final
registration depends on the exact enterprise agent workflow available to the
partner or customer environment.

## Agent Description

Energy Ops Agent optimizes B2B building energy decisions during extreme weather
and utility peak-demand pricing conflicts. It returns source-backed HVAC,
flexible-load shedding, cost-avoidance, protected-risk, and observability trace
outputs for facilities and energy operations teams.

## Invocation Guidance

Invoke this agent when a user asks to:

- optimize a building during a heat dome or other extreme weather event
- resolve occupant-safety versus energy-cost conflicts
- run rare-event simulation cases
- explain load-level demand-response recommendations from grounded data

Do not invoke this agent for:

- unrelated general knowledge questions
- tasks requiring unapproved external side effects
- requests without specific building, weather, pricing, and occupancy context

## Deployment Requirement

Deploy the agent API before registering or exposing it through Gemini
Enterprise. The expected runtime endpoint is a Google Cloud-hosted HTTPS
service backed by Cloud Run or another approved Google Cloud runtime.

For A2A interoperability, deploy `startup_ops_agent.a2a_app:a2a_app`. The
well-known agent card is served from:

```text
/.well-known/agent-card.json
```

## Governance

The agent has deterministic controls for:

- source ID preservation
- deterministic safety-first conflict resolution
- load-level demand-response allocation
- observability trace generation
