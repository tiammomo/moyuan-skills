# Frontend Docs Command Copy Iteration

This temporary note tracks the next frontend/backend iteration for making doc action panels easier to use once the commands are visible.

## Goals

- [x] Add copy-friendly command affordances to doc action panels so repo commands are easier to reuse
- [x] Reuse or extend shared action-panel helpers without changing the underlying command sources
- [x] Extend Playwright coverage to at least one command-copy interaction
- [x] Update README and related docs, run verification, then delete this note when the iteration is complete

## Current Status

- Skill, teaching, and project detail pages now expose action panels with concrete repo commands and next-step links.
- Action panels now provide lightweight copy buttons for repo commands while keeping the shared command source data unchanged.
- Playwright now exercises a real command-copy interaction against the integrated frontend/backend flow.
