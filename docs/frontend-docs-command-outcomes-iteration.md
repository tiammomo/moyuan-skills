# Frontend Docs Command Outcomes Iteration

This temporary note tracks the next frontend/backend iteration for making doc action panels clearer about what success looks like after each command.

## Goals

- [ ] Add expected-outcome cues to doc action panels so readers know what each command should produce or confirm
- [ ] Reuse the existing shared command sources and sequence presentation, only layering outcome messaging on top
- [ ] Extend Playwright coverage to confirm at least one command outcome hint appears in the integrated docs flow
- [ ] Update README and related docs, run verification, then delete this note when the iteration is complete

## Current Status

- Skill, teaching, and project detail pages now expose action panels with ordered runbook cues and copy buttons.
- Action panels still stop at “what to run” and “when to run it”; they do not yet tell readers what success or completion should look like after each command.
