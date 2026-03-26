# Market Installed History Alert Iteration

This temporary note tracks the next installed-state history alert iteration for the local skills market client.

## Goals

- [ ] Add alert/gating support for unusually large installed baseline history transitions
- [ ] Wire the alert workflow into the unified CLI, docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now archive, restore, retain, verify, diff, and report installed baseline history entries.
- Maintainers can already review history manually, but there is still no policy layer that highlights when a retained transition looks unusually large or risky.
- The next gap is history alerting: the client should be able to flag oversized entry-to-entry changes so maintainers can spot risky baseline promotions quickly.
