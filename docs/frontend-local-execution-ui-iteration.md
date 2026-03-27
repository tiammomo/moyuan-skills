# Frontend Local Execution UI Iteration

This iteration follows the completed backend local mutation API pass.

## Goal

Wire the existing skill and bundle install surfaces to the new backend mutation APIs while keeping safe copy-command fallbacks.

## Scope

### 1. Add frontend execution actions for skill detail

- keep the existing copy-command affordance
- add an explicit `Run via backend` action
- show pending, success, and failure states
- link the UI to `POST /api/v1/local/skills/install`

### 2. Add frontend execution actions for bundle detail

- keep the existing local bundle command panel
- add `Run via backend` for bundle install
- poll `GET /api/v1/local/jobs/{job_id}`
- surface backend summary and target-root information

### 3. Add shared job-state presentation

- create a reusable local job status card
- show `queued`, `running`, `succeeded`, and `failed`
- expose stdout/stderr snippets in a review-friendly way

### 4. Preserve honest fallbacks

- command-copy actions stay visible even after execution buttons land
- no UI should imply remote install support yet

## Acceptance criteria

- a user can trigger a local skill install from the frontend
- a user can trigger a local bundle install from the frontend
- job progress and completion are visible without leaving the page
- copy-command fallbacks remain available

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python -m compileall backend`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
