# Frontend Docs Command Troubleshooting Iteration

This temporary note tracks the next frontend/backend iteration for making doc action panels better at helping readers recover when a command does not produce the expected result.

## Goals

- [ ] Add troubleshooting cues to doc action panels so each command can explain what to check first when the expected outcome is missing
- [ ] Reuse the existing ordered runbook, prerequisites, expected outcomes, and artifact hints instead of introducing a separate command widget
- [ ] Extend Playwright coverage to confirm at least one troubleshooting hint appears in the integrated docs flow
- [ ] Update README and related docs, run verification, then delete this note when the iteration is complete

## Current Status

- Skill, teaching, and project detail pages now expose action panels with ordered runbook cues, prerequisite hints, expected-outcome hints, artifact/output hints, and copy buttons.
- Readers still do not get a first troubleshooting step when a command finishes without the expected artifact or pass signal.
