# Market Installed History Waiver Source Reconcile Verify Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-verify iteration for the local skills market client.

## Goals

- [ ] Verify executed source-reconcile repairs against the latest reviewed reconcile artifacts without rerunning the full smoke workflow
- [ ] Expose the source-reconcile-verify workflow through the unified CLI, README/docs, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now audit waiver source drift, build reconcile artifacts, and execute reviewed source-reconcile repairs back onto governance source mirrors with current-source hash checks.
- The next gap is post-execution verification: maintainers can repair source drift, but the repo still lacks a dedicated workflow to prove those repaired source mirrors still match the reviewed reconcile target after the execution step has finished.
