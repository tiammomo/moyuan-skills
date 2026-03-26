# Market Installed History Waiver Source Reconcile Waiver Apply Gate Waiver Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-waiver-apply-gate-waiver iteration for the local skills market client.

## Goals

- [ ] Add reusable waivers for source-reconcile gate waiver apply findings so specific known exceptions can be approved without weakening the whole policy
- [ ] Expose the apply-gate waiver workflow through governance checks, the unified CLI, README/docs, and smoke pipeline
- [ ] Reuse the waiver model for future audit and remediation steps on apply-gate findings
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now generate apply reports and evaluate them with release or review-handoff gate policies.
- The next gap is selective exceptions: maintainers still need a way to approve specific apply-gate findings without switching the entire workflow to a weaker policy profile.
