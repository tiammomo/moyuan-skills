# Issue Triage Input Contract

## Required CSV Columns

The bundled script expects a header row with these columns:

- `id`
- `title`
- `severity`
- `status`
- `owner`
- `action`
- `customer_impact`
- `highlight`

The script ignores extra columns, but these eight fields should always be present.

## Allowed Values

Supported `severity` values:

- `critical`
- `high`
- `medium`
- `low`

Supported `status` values:

- `open`
- `in-progress`
- `blocked`
- `backlog`
- `resolved`

## Grouping Rules

The generator maps issues into four sections:

- Hot Issues
  `critical` or `high` issues that are not resolved, plus any row marked with `highlight=true`
- Needs Decision
  issues whose `action` starts with `decision:`
- Assigned Follow-ups
  issues that are not resolved or backlog, and already have an owner
- Backlog Watch
  issues in `backlog`, or lower-severity work that still deserves visibility

## Highlight Column

`highlight` accepts truthy values such as:

- `true`
- `yes`
- `1`

Rows marked as highlights are surfaced before the normal grouping heuristics.

## Example

See `assets/sample-issues.csv` for a runnable example input.

