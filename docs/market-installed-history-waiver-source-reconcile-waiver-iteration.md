# Market Installed History Waiver Source Reconcile Waiver Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-waiver iteration for the local skills market client.

## Goals

- [ ] Add reusable waivers for source-reconcile gate findings so teams can temporarily accept known drift or blocked states without rewriting policy profiles
- [ ] Expose the source-reconcile-waiver workflow through the unified CLI, README/docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now audit waiver source drift, build reconcile artifacts, execute reviewed repairs, verify staged or written results, aggregate the workflow into a single report pack, enforce it with a reusable gate, and select behavior through named policy profiles.
- The next gap is exception handling: teams still need a way to approve temporary source-reconcile findings for specific workflows without weakening an entire policy profile, so the repo needs source-reconcile gate waivers.
