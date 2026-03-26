# Market Installed History Waiver Source Reconcile Report Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-report iteration for the local skills market client.

## Goals

- [ ] Aggregate source-audit, source-reconcile, execution, and verification artifacts into a single reviewable report pack
- [ ] Expose the source-reconcile-report workflow through the unified CLI, README/docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now audit waiver source drift, build reconcile artifacts, execute reviewed repairs, and verify staged or written results against the reviewed reconcile target.
- The next gap is reviewer ergonomics: maintainers still need to open multiple JSON/Markdown artifacts to understand one full source-reconcile cycle, so the repo needs a consolidated report workflow for handoff and audit trails.
