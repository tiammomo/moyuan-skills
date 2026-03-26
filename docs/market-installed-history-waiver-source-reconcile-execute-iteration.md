# Market Installed History Waiver Source Reconcile Execute Iteration

This temporary note tracks the next installed-state history waiver source-reconcile-execute iteration for the local skills market client.

## Goals

- [ ] Turn source-reconcile restore artifacts into guarded execution helpers that can stage or write source-reconcile repairs safely
- [ ] Expose the source-reconcile-execute workflow through the unified CLI, documentation, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now detect source drift and package restore-target or restore-delete artifacts that describe how to recover reviewed waiver source files.
- The next gap is execution: maintainers can review restore artifacts, but the repo still lacks a built-in workflow to stage or apply those source-reconcile repairs back onto governance source mirrors with safety checks.
