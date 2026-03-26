# Market Installed History Waiver Source Reconcile Waiver Apply Verify Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-waiver-apply-verify iteration for the local skills market client.

## Goals

- [ ] Verify source-reconcile gate waiver apply execution summaries against the current target root and report drift clearly
- [ ] Reuse the recorded execution metadata for governance review, smoke coverage, and future gate automation
- [ ] Expose the source-reconcile-waiver-apply-verify workflow through the unified CLI, README/docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now build source-reconcile gate waiver apply packs and execute them safely in stage/write modes.
- The next gap is verification: maintainers still need a direct way to confirm that written or staged targets still match the reviewed apply execution summary after the fact.
