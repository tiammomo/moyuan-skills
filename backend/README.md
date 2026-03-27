# Moyuan Skills Python Backend

This backend exposes the existing `moyuan-skills` repo as a frontend-friendly API.

It is designed for the current Next.js frontend under `frontend/`, and it reads the same real assets that the repo already generates:

- `dist/market/index.json`
- `dist/market/channels/*.json`
- `dist/market/install/*.json`
- `skills/*/market/skill.json`
- `docs/*.md`
- `docs/teaching/*.md`
- `bundles/*.json`

## Why this backend exists

The current frontend already has a clear information architecture:

- homepage needs market index + featured channel data
- skills pages need search/filterable skill summaries
- skill detail pages need manifest + install spec + markdown docs
- bundle pages need real bundle composition + install metadata
- docs pages need a catalog of teaching, skill, and project docs, plus a unified searchable doc list

This backend keeps those shapes stable while moving file access out of the frontend.

The shared frontend data layer now also derives related-doc navigation, doc-specific context panels, and copy-friendly action-oriented next-step commands from the docs catalog plus skill metadata, so detail pages can keep readers moving without introducing extra recommendation-specific APIs. The frontend now turns those commands into lightweight ordered runbooks with prerequisite, expected-outcome, and artifact/output cues directly in the doc detail UI.
The backend now also exposes the first local mutation APIs for skill and bundle installation jobs, so the frontend can evolve from copy-first guidance toward true execution flows without reimplementing the installer logic.

## Run

```text
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 38083
```

If the repo root is not the current working directory, set:

```text
set MOYUAN_SKILLS_REPO_ROOT=D:\moyuan\moyuan-skills
```

Optional CORS override:

```text
set MOYUAN_SKILLS_API_CORS=http://127.0.0.1:33003,http://localhost:33003
```

## Core endpoints

```text
GET /health
GET /api/v1/meta/repo
GET /api/v1/market/index
GET /api/v1/market/channels/{channel}
GET /api/v1/market/skills
GET /api/v1/market/skills/{name}
GET /api/v1/market/skills/{name}/install-spec
GET /api/v1/market/skills/{name}/doc
GET /api/v1/market/categories
GET /api/v1/market/tags
GET /api/v1/market/bundles
GET /api/v1/market/bundles/{bundle_id}
POST /api/v1/local/skills/install
POST /api/v1/local/bundles/install
GET /api/v1/local/jobs/{job_id}
GET /api/v1/docs/catalog
GET /api/v1/docs/teaching/{doc_id}
GET /api/v1/docs/project/{doc_id}

`GET /api/v1/docs/catalog` now returns per-family doc arrays plus a flattened `all_docs` list for frontend filtering.
```

Local mutation notes:

- the first pass intentionally covers local install jobs only
- the backend reuses `scripts/install_skill.py` and `scripts/install_skill_bundle.py`
- the response returns a `job_id`, and clients poll `GET /api/v1/local/jobs/{job_id}` for completion
- the frontend now wires skill install and bundle install through local proxy routes while keeping copy-first fallbacks visible

## Suggested frontend mapping

- `frontend/app/page.tsx` -> `/api/v1/market/index`, `/api/v1/market/channels/stable`, `/api/v1/market/channels/beta`, `/api/v1/market/categories`
- `frontend/app/skills/page.tsx` -> `/api/v1/market/skills`, `/api/v1/market/categories`, `/api/v1/market/tags`
- `frontend/app/skills/[name]/page.tsx` -> `/api/v1/market/skills/{name}`
- `frontend/app/channels/[channel]/page.tsx` -> `/api/v1/market/channels/{channel}`
- `frontend/app/bundles/page.tsx` -> `/api/v1/market/bundles`
- `frontend/app/bundles/[id]/page.tsx` -> `/api/v1/market/bundles/{bundle_id}`
- `frontend/app/docs/page.tsx` -> `/api/v1/docs/catalog`
- `frontend/app/docs/teaching/page.tsx` -> `/api/v1/docs/catalog`
- `frontend/app/docs/teaching/[slug]/page.tsx` -> `/api/v1/docs/teaching/{doc_id}`
- `frontend/app/docs/project/[slug]/page.tsx` -> `/api/v1/docs/project/{doc_id}`

## Frontend API mode

The frontend now supports both:

- local filesystem mode
- backend API mode via `SKILLS_MARKET_API_BASE_URL`

Example:

```text
set SKILLS_MARKET_API_BASE_URL=http://127.0.0.1:38083
npm run dev:local --prefix frontend
```

Recommended local ports:

- frontend: `33003`
- backend: `38083`

## Playwright end-to-end verification

The repo now includes a Playwright flow that starts this FastAPI backend and the Next.js frontend together, then validates homepage, skills, bundle, docs search/filter, teaching, project-doc, ordered command-runbook, prerequisite, expected-outcome, artifact/output, and command-copy flows against the real API:

```text
npx playwright install chromium --prefix frontend
npm run build --prefix frontend
npm run e2e --prefix frontend
npm run capture:readme-screenshots --prefix frontend
```

## Current execution status

What is now available:

- repo-backed read APIs for market, bundle, and docs flows
- local mutation APIs for skill install, bundle install, and job polling
- backend smoke coverage for both repository reads and local install jobs

What is still next:

- local update and remove mutation APIs
- installed-state read APIs and follow-up lifecycle actions
- remote registry download and install support
