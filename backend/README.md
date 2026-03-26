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

The shared frontend data layer now also derives related-doc navigation, doc-specific context panels, and copy-friendly action-oriented next-step commands from the docs catalog plus skill metadata, so detail pages can keep readers moving without introducing extra recommendation-specific APIs. The frontend now turns those commands into lightweight ordered runbooks with prerequisite and expected-outcome cues directly in the doc detail UI.

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
GET /api/v1/docs/catalog
GET /api/v1/docs/teaching/{doc_id}
GET /api/v1/docs/project/{doc_id}

`GET /api/v1/docs/catalog` now returns per-family doc arrays plus a flattened `all_docs` list for frontend filtering.
```

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

The repo now includes a Playwright flow that starts this FastAPI backend and the Next.js frontend together, then validates homepage, skills, bundle, docs search/filter, teaching, project-doc, ordered command-runbook, prerequisite, expected-outcome, and command-copy flows against the real API:

```text
npx playwright install chromium --prefix frontend
npm run build --prefix frontend
npm run e2e --prefix frontend
```
