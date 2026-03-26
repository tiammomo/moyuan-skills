# Frontend Docs Command Prerequisites Iteration

This temporary note tracks the next frontend/backend iteration for making doc action panels clearer about what setup or prerequisites a reader needs before running a command.

## Goals

- [ ] Add prerequisite cues to doc action panels so readers know when a command depends on setup, generated assets, or prior steps
- [ ] Reuse the existing shared command sources, sequence cues, and expected outcomes, only layering prerequisite messaging on top
- [ ] Extend Playwright coverage to confirm at least one prerequisite hint appears in the integrated docs flow
- [ ] Update README and related docs, run verification, then delete this note when the iteration is complete

## Current Status

- Skill, teaching, and project detail pages now expose action panels with ordered runbook cues, expected-outcome hints, and copy buttons.
- Action panels still assume the reader already knows which setup or prior artifacts are required before running each command.
