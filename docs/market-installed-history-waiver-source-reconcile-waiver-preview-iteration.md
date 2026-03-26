# Market Installed History Waiver Source Reconcile Waiver Preview Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-waiver-preview iteration for the local skills market client.

## Goals

- [x] Turn source-reconcile gate waiver execution drafts into review-friendly previews that show how renewal, retarget, replacement, or policy-review drafts differ from the source waiver files
- [x] Expose the source-reconcile-waiver-preview workflow through the unified CLI, README/docs, and smoke pipeline
- [x] Run validation, then delete this note after the iteration is fully complete

## Current Status

- Completed on 2026-03-26.
- The client can now compare source-reconcile gate waiver execution drafts against the current waiver sources and emit per-waiver preview JSON/Markdown artifacts.
- The unified CLI, smoke pipeline, README, governance docs, registry docs, repo commands, and teaching docs now all describe the `preview-installed-history-waiver-source-reconcile-waiver-execution` workflow.
