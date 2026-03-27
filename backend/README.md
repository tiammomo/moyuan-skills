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
The backend now exposes a complete local lifecycle API layer plus the first remote registry install API layer for skills and bundles, so the frontend can evolve from copy-first guidance toward true execution flows without reimplementing installer or lifecycle logic. The frontend remote execution cards now add a first trust-and-approval pass on top of those APIs, so remote jobs no longer look unconditional.

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
POST /api/v1/local/skills/update
POST /api/v1/local/skills/remove
POST /api/v1/local/bundles/install
POST /api/v1/local/bundles/update
POST /api/v1/local/bundles/remove
POST /api/v1/local/state/doctor
POST /api/v1/local/state/repair
POST /api/v1/registry/skills/install
POST /api/v1/registry/bundles/install
POST /api/v1/registry/cleanup
GET /api/v1/local/jobs/{job_id}
GET /api/v1/local/state
GET /api/v1/docs/catalog
GET /api/v1/docs/teaching/{doc_id}
GET /api/v1/docs/project/{doc_id}

`GET /api/v1/docs/catalog` now returns per-family doc arrays plus a flattened `all_docs` list for frontend filtering.
```

Local lifecycle notes:

- the backend reuses the existing lifecycle scripts under `scripts/`
- the response returns a `job_id`, and clients poll `GET /api/v1/local/jobs/{job_id}` for completion
- the frontend now wires skill install and bundle install through local proxy routes while keeping copy-first fallbacks visible
- update/remove/state/doctor/repair APIs are now consumed by the first frontend installed-state lifecycle surfaces on skill and bundle detail pages

Remote registry notes:

- the backend can now resolve `skill id + registry URL` and `bundle id + registry URL`
- remote artifacts are downloaded into a deterministic cache root before install
- remote install still reuses the same local installer semantics after staging, including checksum and lifecycle checks
- the frontend skill and bundle detail pages now proxy these remote install jobs through Next.js API routes
- the frontend now requires explicit in-page approval before those remote jobs are submitted
- remote execution cards now surface publisher verification, review status, lifecycle status, and provenance hints before execution starts
- the backend now also exposes a cleanup job endpoint so the frontend can clear staged cache or failed target roots after a failed remote run

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

The repo now includes a Playwright flow that starts this FastAPI backend, the Next.js frontend, and a temporary hosted registry fixture together, then validates homepage, skills, bundle, docs search/filter, teaching, project-doc, ordered command-runbook, prerequisite, expected-outcome, artifact/output, command-copy, and remote registry install flows against the real API:

```text
npx playwright install chromium --prefix frontend
npm run build --prefix frontend
npm run e2e --prefix frontend
npm run capture:readme-screenshots --prefix frontend
```

## Current execution status

What is now available:

- repo-backed read APIs for market, bundle, and docs flows
- local lifecycle APIs for skill and bundle install, update, remove, state, doctor, repair, and job polling
- remote registry install APIs for skill and bundle downloads over HTTP
- frontend-consumable remote install flows for skill and bundle detail pages
- frontend trust, approval, retry, and cleanup affordances for the first remote install failure paths
- frontend-consumable installed-state read, update, remove, doctor, and low-risk repair flows on skill and bundle detail pages
- backend smoke coverage for repository reads plus local, remote, doctor, repair, and cleanup lifecycle jobs

What is still next:

- deeper installed-state product surfaces such as baseline history and governance views
- deeper remote policy gating and rollback/reconciliation surfaces for remote installs
