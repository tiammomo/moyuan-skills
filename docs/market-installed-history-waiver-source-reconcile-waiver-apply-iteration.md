# Market Installed History Waiver Source Reconcile Waiver Apply Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-waiver-apply iteration for the local skills market client.

## Goals

- [ ] Turn source-reconcile gate waiver previews into apply-ready artifacts such as per-waiver targets, per-waiver patches, and a combined patch bundle
- [ ] Expose the source-reconcile-waiver-apply workflow through the unified CLI, README/docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now audit source-reconcile gate waivers, remediate their findings, materialize execution drafts, and compare those drafts against the current waiver sources.
- The next gap is apply packaging: maintainers still need a structured way to turn the reviewed preview output into patch-ready artifacts before they update `governance/source-reconcile-gate-waivers/`.
