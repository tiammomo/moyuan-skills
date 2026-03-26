# Market Installed History Waiver Source Reconcile Waiver Apply Gate Waiver Audit Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-waiver-apply-gate-waiver-audit iteration for the local skills market client.

## Goals

- [ ] Audit source-reconcile gate waiver apply waivers for expired, unmatched, stale, or policy-mismatch records
- [ ] Expose the apply-gate waiver audit workflow through governance checks, the unified CLI, README/docs, and smoke pipeline
- [ ] Reuse the audit output for follow-up remediation and execution planning
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now list and apply targeted waivers to source-reconcile gate waiver apply findings.
- The next gap is lifecycle governance: maintainers still need a way to audit whether those apply-gate waivers are expired, no longer match real findings, or are attached to the wrong policy profile.
