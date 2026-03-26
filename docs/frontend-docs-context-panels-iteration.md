# Frontend Docs Context Panels Iteration

This temporary note tracks the next frontend/backend iteration for making each doc detail page feel more actionable once a reader arrives there.

## Goals

- [ ] Add context panels to doc detail pages so skill, teaching, and project docs expose next-step metadata instead of only markdown
- [ ] Reuse or extend shared data-layer helpers for doc-specific context where needed
- [ ] Extend Playwright coverage to at least one context-panel flow
- [ ] Update README and related docs, run verification, then delete this note when the iteration is complete

## Current Status

- The docs center now supports repo-backed detail pages, searchable/filterable browsing, and related navigation across all doc kinds.
- Individual doc detail pages still focus almost entirely on markdown content and do not yet surface doc-specific context such as install entrypoints, learning-path cues, or source metadata in a dedicated panel.
