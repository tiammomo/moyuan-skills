# Frontend Docs Command Sequences Iteration

This temporary note tracks the next frontend/backend iteration for turning copied doc commands into clearer step-by-step runbooks.

## Goals

- [ ] Add sequence cues to doc action panels so multi-command flows read like an ordered runbook
- [ ] Reuse the existing shared command sources and only layer sequence metadata or presentation on top
- [ ] Extend Playwright coverage to confirm at least one ordered command sequence appears in the integrated docs flow
- [ ] Update README and related docs, run verification, then delete this note when the iteration is complete

## Current Status

- Skill, teaching, and project detail pages now expose action panels with concrete repo commands, next-step links, and copy buttons.
- Multi-command panels still render as flat command lists, so readers do not yet get an explicit “start here / then validate / finally verify” sequence.
