# Incident Input Contract

## Required Top-Level Fields

The bundled script expects these top-level JSON keys:

- `incident_id`
- `service`
- `severity`
- `start_time`
- `end_time`
- `summary`
- `customer_impact`
- `root_cause`
- `timeline`
- `action_items`
- `follow_up_risks`

## Severity

Supported severity values:

- `sev1`
- `sev2`
- `sev3`
- `sev4`

## Timeline

`timeline` must be a list of objects with:

- `time`
- `event`

Optional:

- `owner`

The generator preserves timeline order, so the input should already be chronological.

## Action Items

`action_items` must be a list of objects with:

- `title`
- `owner`

Optional:

- `status`
- `due_date`

## Follow-up Risks

`follow_up_risks` may be a list of strings or objects with `title` and optional `description`.

## Example

See `assets/sample-incident.json` for a runnable example input.

