# Market Installed History Waiver Audit Iteration

This temporary note tracks the next installed-state history waiver-audit iteration for the local skills market client.

## Goals

- [ ] Add waiver audit checks for expired, unmatched, or stale installed baseline history waivers
- [ ] Wire the waiver-audit workflow into the unified CLI, docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now archive, restore, retain, verify, diff, report, alert, apply named policy profiles, and reuse explicit waiver records for installed baseline history entries.
- Maintainers can already distinguish approved exceptions from unexpected drift, but there is still no dedicated audit step for spotting expired waivers or waiver records that no longer match any retained transition.
- The next gap is waiver audit: the client should surface stale or expired waivers before they silently accumulate in governance assets.
