# Market Installed History Waiver Remediation Iteration

This temporary note tracks the next installed-state history waiver-remediation iteration for the local skills market client.

## Goals

- [ ] Add remediation guidance for expired, unmatched, or stale installed baseline history waivers
- [ ] Wire the remediation workflow into the unified CLI, docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now archive, restore, retain, verify, diff, report, alert, apply named policy profiles, reuse explicit waiver records, and audit waiver health for installed baseline history entries.
- Maintainers can already see which waivers are expired, unmatched, or stale, but there is still no dedicated remediation workflow that suggests whether a waiver should be renewed, cleaned up, or replaced.
- The next gap is waiver remediation: the client should turn waiver audit findings into explicit follow-up guidance instead of leaving the maintainer to infer the next action manually.
