# Backend Local Lifecycle API Iteration

This iteration follows the completed frontend local execution UI pass.

## Goal

Extend the backend mutation layer beyond install so the frontend can grow from "launch install jobs" into a fuller installed-state client surface.

## Scope

### 1. Add local skill lifecycle endpoints

- add backend `update` and `remove` endpoints for skills
- keep the same job-oriented execution model used by install
- reuse the existing `scripts/` lifecycle commands instead of duplicating logic

### 2. Add local bundle lifecycle endpoints

- add backend `update` and `remove` endpoints for bundles
- expose job summaries that mention the affected bundle and target root
- keep copy-first frontend fallbacks available until the UI wiring lands

### 3. Add installed-state read endpoints

- expose an installed-state summary API for skills and bundles
- expose enough metadata for future UI surfaces such as installed pages, doctor pages, and lifecycle summaries
- do not expose internal planning docs or unstable repo notes

### 4. Preserve honest recovery boundaries

- keep approval, provenance, and remote download out of scope for this pass
- do not imply remote install support
- make failures readable and reusable in the UI

## Acceptance criteria

- the backend exposes local update/remove endpoints for skills and bundles
- the backend exposes at least one installed-state read endpoint for UI consumption
- the existing install job model still works unchanged
- docs and roadmap clearly explain what is now executable and what still remains copy-first

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python -m compileall backend`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
