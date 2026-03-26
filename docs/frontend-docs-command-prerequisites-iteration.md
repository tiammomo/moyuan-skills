# Frontend Docs Command Prerequisites Iteration

This temporary note tracks the next frontend/backend iteration for making doc action panels clearer about what setup or prerequisites a reader needs before running a command.

## Goals

- [x] Add prerequisite cues to doc action panels so readers know when a command depends on setup, generated assets, or prior steps
- [x] Reuse the existing shared command sources, sequence cues, and expected outcomes, only layering prerequisite messaging on top
- [x] Extend Playwright coverage to confirm at least one prerequisite hint appears in the integrated docs flow
- [x] Update README and related docs, run verification, then delete this note when the iteration is complete

## Current Status

- Skill, teaching, and project detail pages now expose action panels with ordered runbook cues, prerequisite hints, expected-outcome hints, and copy buttons.
- Action panels now explain what needs to be ready before each command, rather than assuming the reader already knows the setup state.
