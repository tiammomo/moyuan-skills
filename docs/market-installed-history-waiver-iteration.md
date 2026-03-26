# Market Installed History Waiver Iteration

This temporary note tracks the next installed-state history waiver iteration for the local skills market client.

## Goals

- [ ] Add reusable waiver records for accepted installed baseline history alerts
- [ ] Wire the waiver workflow into the unified CLI, docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now archive, restore, retain, verify, diff, report, alert, and apply named policy profiles to installed baseline history entries.
- Maintainers can already standardize transition gates with reusable policies, but there is still no structured way to record that a reviewed alert was intentionally accepted.
- The next gap is waiver handling: the client should support explicit history alert waivers so teams can distinguish approved exceptions from unexpected drift.
