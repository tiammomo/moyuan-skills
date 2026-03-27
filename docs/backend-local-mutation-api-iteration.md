# Backend Local Mutation API Iteration

This iteration follows the completed honest local-command UI pass.

## Goal

Add the first backend mutation APIs so the frontend can move from command-copy guidance toward real local execution.

## Scope

### 1. Add backend job execution primitives

- define a lightweight job model for local script execution
- return `job_id`, `status`, `summary`, and artifact references
- keep execution asynchronous from the frontend point of view

### 2. Ship the first mutation endpoints

- `POST /api/v1/local/skills/install`
- `POST /api/v1/local/bundles/install`
- `GET /api/v1/local/jobs/{job_id}`

The first pass can stay intentionally narrow:

- local market only
- no remote registry fetch yet
- no approval flow yet

### 3. Reuse existing scripts

- call the existing `scripts/install_skill.py`
- call the existing `scripts/install_skill_bundle.py`
- avoid duplicating install logic inside FastAPI handlers

### 4. Frontend follow-up contract

- define the request and response shape needed by the current skill and bundle detail pages
- keep current copy-command affordances as a safe fallback until mutation flows are fully tested

## Acceptance criteria

- a frontend client can request a local skill install through the backend
- a frontend client can request a local bundle install through the backend
- job status can be polled from the UI
- existing Playwright coverage stays green

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python -m compileall backend`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
