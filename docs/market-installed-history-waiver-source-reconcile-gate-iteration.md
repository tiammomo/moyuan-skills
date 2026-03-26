# Market Installed History Waiver Source Reconcile Gate Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-gate iteration for the local skills market client.

## Goals

- [ ] Turn the source-reconcile report into a reusable gate that fails on incomplete handoff, blocked execution, or verification drift
- [ ] Expose the source-reconcile-gate workflow through the unified CLI, README/docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now audit waiver source drift, build reconcile artifacts, execute reviewed repairs, verify staged or written results, and aggregate the full chain into a single report pack.
- The next gap is automation: reviewers can read one report, but the repo still lacks a single gate command that can enforce “report complete and verification clean” in CI or release workflows.
