# Security And Enterprise Controls

## Identity And Access

- Runtime should use a dedicated Google Cloud service account.
- External tool adapters must authorize by tenant, building, and source system.
- Write actions to BMS or utility systems remain disabled unless buyer
  configuration enables approval workflow integration.

## Secrets

- No credentials are stored in the repository.
- API keys and connector credentials must be supplied through Secret Manager or
  runtime environment configuration.
- Logs must not include tokens, passwords, private keys, raw occupancy details,
  or restricted facility records.

## Tenant Isolation

Production adapters must scope every query and action by:

- tenant ID
- building ID
- source-system permission scope
- source system
- weather, pricing, occupancy, or plan ID

## Auditability

Production service deployments should write audit events for:

- energy plan generation
- simulation execution
- selected load-shed decisions
- source IDs used
- tenant and building scope

## Failure Mode

The system fails closed for missing energy records, invalid data, and unavailable
source context.
