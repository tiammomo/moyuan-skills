# Market Installed History Waiver Source Reconcile Policy Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-policy iteration for the local skills market client.

## Goals

- [ ] Add reusable policy profiles for the source-reconcile gate so teams can choose stricter or more permissive passing states without hand-writing flags
- [ ] Expose the source-reconcile-policy workflow through the unified CLI, README/docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now audit waiver source drift, build reconcile artifacts, execute reviewed repairs, verify staged or written results, aggregate the workflow into a single report pack, and enforce it with a reusable gate.
- The next gap is policy reuse: maintainers still need to spell out gate behavior inline, so the repo needs named source-reconcile gate profiles that can be shared across CI, release, and audit workflows.
