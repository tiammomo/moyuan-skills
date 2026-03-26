# Market Installed History Waiver Source Reconcile Waiver Audit Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-waiver-audit iteration for the local skills market client.

## Goals

- [ ] Audit reusable source-reconcile gate waivers for expired, unmatched, stale, or policy-mismatch cases
- [ ] Expose the source-reconcile-waiver-audit workflow through the unified CLI, README/docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now apply named source-reconcile gate policies and approved gate waivers, so strict release flows can accept a scoped exception without weakening the whole policy profile.
- The next gap is governance hygiene: once source-reconcile gate waivers exist, the repo needs an audit workflow that shows when those waivers are expired, no longer match current source-reconcile reports, or reference the wrong policy.
