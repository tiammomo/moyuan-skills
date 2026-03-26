# Market Installed History Waiver Apply Iteration

This temporary note tracks the next installed-state history waiver-apply iteration for the local skills market client.

## Goals

- [ ] Turn reviewed waiver preview artifacts into safe apply-ready patch outputs for governance source files
- [ ] Expose the apply workflow through the unified CLI, documentation, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now generate remediation guidance, execution drafts, and source-vs-draft previews for installed history waivers.
- The next gap is apply support: reviewers can see exactly what should change, but the repo still lacks a safe way to turn an approved preview into a patch or apply-ready artifact.
