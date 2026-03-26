# Market Installed History Waiver Source Reconcile Waiver Preview Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-waiver-preview iteration for the local skills market client.

## Goals

- [ ] Turn source-reconcile gate waiver execution drafts into review-friendly previews that show how renewal, retarget, replacement, or policy-review drafts differ from the source waiver files
- [ ] Expose the source-reconcile-waiver-preview workflow through the unified CLI, README/docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now audit source-reconcile gate waivers, remediate their findings, and materialize execution drafts under a dedicated execution artifact root.
- The next gap is review diffing: maintainers still need a compact way to compare those generated drafts against the current waiver sources before they move on to apply-ready changes.
