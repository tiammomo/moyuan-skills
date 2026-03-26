# Market Installed History Waiver Apply Execute Iteration

This temporary note tracks the next installed-state history waiver-apply-execute iteration for the local skills market client.

## Goals

- [ ] Turn reviewed waiver apply packs into guarded execution helpers that can stage or write governance source changes safely
- [ ] Expose the apply-execute workflow through the unified CLI, documentation, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now generate remediation guidance, execution drafts, previews, and apply-ready patch bundles for installed history waivers.
- The next gap is guarded execution: maintainers can review patch artifacts, but the repo still lacks a built-in workflow to apply an approved pack back onto governance source files with safety checks.
