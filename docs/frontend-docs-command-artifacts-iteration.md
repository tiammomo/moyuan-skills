# Frontend Docs Command Artifacts Iteration

This temporary note tracks the next frontend/backend iteration for making doc action panels clearer about which files, reports, or generated artifacts each command produces.

## Goals

- [ ] Add artifact cues to doc action panels so readers know which output files or reports to expect after a command finishes
- [ ] Reuse the existing shared command sources, sequence cues, prerequisites, and expected outcomes, only layering artifact messaging on top
- [ ] Extend Playwright coverage to confirm at least one artifact hint appears in the integrated docs flow
- [ ] Update README and related docs, run verification, then delete this note when the iteration is complete

## Current Status

- Skill, teaching, and project detail pages now expose action panels with ordered runbook cues, prerequisite hints, expected-outcome hints, and copy buttons.
- Action panels still do not tell readers where to find the output artifact, report, or generated file after a command completes.
