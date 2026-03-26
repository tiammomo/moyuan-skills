# Market Installed History Waiver Source Reconcile Iteration

This temporary note tracks the next installed-state history waiver source-reconcile iteration for the local skills market client.

## Goals

- [ ] Turn source-audit drift findings into reconcile-ready artifacts that can restore governance waiver files back to their latest reviewed state
- [ ] Expose the source-reconcile workflow through the unified CLI, documentation, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now audit reviewed waiver source files and clearly classify them as pending, applied, manual-review-only, or drifted.
- The next gap is reconcile follow-up: maintainers can detect post-execute drift, but the repo still lacks a built-in way to package the expected source restore steps after an audit finding appears.
