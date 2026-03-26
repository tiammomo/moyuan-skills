# Market Installed History Policy Iteration

This temporary note tracks the next installed-state history policy iteration for the local skills market client.

## Goals

- [ ] Add reusable policy profiles for installed baseline history alerts
- [ ] Wire the policy-profile workflow into the unified CLI, docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now archive, restore, retain, verify, diff, report, and alert on installed baseline history entries.
- Maintainers can already run alert thresholds directly, but the thresholds still have to be repeated on the command line each time.
- The next gap is policy reuse: the client should support named history alert profiles so teams can apply consistent transition gates without duplicating threshold flags by hand.
