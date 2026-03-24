# Release Note Input Contract

## Required Top-Level Fields

The bundled script expects JSON input with these top-level keys:

- `product_name`
- `version`
- `release_date`
- `summary`
- `changes`
- `breaking_changes`
- `known_issues`

All fields except `changes`, `breaking_changes`, and `known_issues` should be strings.

## Changes Array

Each item in `changes` should be an object with:

- `type`
- `title`
- `description`

Optional fields:

- `ticket`
- `impact`
- `highlight`

Supported `type` values:

- `feature`
- `improvement`
- `fix`
- `security`
- `docs`
- `internal`

The script groups them into markdown sections. `security` changes are grouped with fixes, while `docs` and `internal` changes are grouped with improvements.

## Highlights

The generator uses items with `highlight: true` first.

If no highlights are marked, it automatically chooses up to three non-internal changes as highlights.

## Breaking Changes and Known Issues

`breaking_changes` and `known_issues` may contain either:

- plain strings
- objects with `title` and optional `description`

That keeps the input flexible while still producing stable markdown output.

## Example

See `assets/sample-release-input.json` for a runnable example input.

