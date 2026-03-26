# Market Installed History Waiver Source Reconcile Waiver Apply Gate Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-waiver-apply-gate iteration for the local skills market client.

## Goals

- [ ] Turn the source-reconcile gate waiver apply report into a reusable gate/handoff signal
- [ ] Add policy/profile support so release and review workflows can choose different apply gate expectations
- [ ] Expose the apply-gate workflow through the unified CLI, README/docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now prepare, execute, verify, and report source-reconcile gate waiver apply workflows end to end.
- The next gap is governance reuse: maintainers still need a single apply-oriented gate that can interpret the report and decide whether the workflow is ready for release or only ready for review handoff.
