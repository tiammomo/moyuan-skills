# Frontend / Backend Integration

## Goal

Make the existing `frontend/` skills market UI run in two modes without changing the route structure:

- local filesystem mode for static repo browsing
- Python backend API mode for real front/back integration

The repo now supports both.

## Current implementation

### Python backend

The backend lives under `backend/` and exposes repo-backed API payloads through FastAPI.

Core endpoints:

- `GET /health`
- `GET /api/v1/market/index`
- `GET /api/v1/market/channels/{channel}`
- `GET /api/v1/market/skills`
- `GET /api/v1/market/skills/{name}`
- `GET /api/v1/market/skills/{name}/install-spec`
- `GET /api/v1/market/skills/{name}/doc`
- `GET /api/v1/market/categories`
- `GET /api/v1/market/tags`
- `GET /api/v1/market/bundles`
- `GET /api/v1/market/bundles/{bundle_id}`
- `GET /api/v1/docs/catalog`
- `GET /api/v1/docs/teaching/{doc_id}`
- `GET /api/v1/docs/project/{doc_id}`

The docs catalog now carries both grouped arrays and a flattened `all_docs` list so the frontend can filter across all doc families without reassembling the payload client-side.
That same shared payload now also supports detail-page related navigation, context panels, and copy-friendly ordered action panels with expected-outcome cues without requiring separate recommendations or metadata endpoints.

The repository layer reads these real assets directly:

- `dist/market/index.json`
- `dist/market/channels/*.json`
- `dist/market/install/*.json`
- `skills/*/market/skill.json`
- `docs/*.md`
- `docs/teaching/*.md`
- `bundles/*.json`

Temporary `docs/*-iteration.md` planning notes are intentionally excluded from the project docs catalog so the frontend only exposes stable user-facing documentation.

### Frontend data layer

`frontend/lib/data.ts` is now the single integration point for the UI.

It supports:

- filesystem mode when `SKILLS_MARKET_API_BASE_URL` is unset
- API mode when `SKILLS_MARKET_API_BASE_URL` points at the FastAPI backend

This keeps the UI components stable while letting Playwright validate a true front/back path.

### Real repo-backed pages

The frontend is no longer limited to file placeholders for the main market flows.

Pages now consume live bundle/docs payloads through the shared data layer:

- `frontend/app/page.tsx`
- `frontend/app/skills/page.tsx`
- `frontend/app/skills/[name]/page.tsx`
- `frontend/app/channels/[channel]/page.tsx`
- `frontend/app/bundles/page.tsx`
- `frontend/app/bundles/[id]/page.tsx`
- `frontend/app/docs/page.tsx`
- `frontend/app/docs/[skill]/page.tsx`
- `frontend/app/docs/teaching/page.tsx`
- `frontend/app/docs/teaching/[slug]/page.tsx`
- `frontend/app/docs/project/[slug]/page.tsx`

## Local run

Recommended local ports:

- frontend: `33003`
- backend: `38083`

### Backend

```text
pip install -r backend/requirements.txt
set MOYUAN_SKILLS_REPO_ROOT=D:\moyuan\moyuan-skills
set MOYUAN_SKILLS_API_CORS=http://127.0.0.1:33003,http://localhost:33003
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 38083
```

### Frontend in API mode

```text
set SKILLS_MARKET_API_BASE_URL=http://127.0.0.1:38083
npm run dev:local --prefix frontend
```

### Frontend in filesystem mode

```text
npm run dev:local --prefix frontend
```

## Playwright full-stack verification

The repo now includes Playwright coverage for the combined flow.

Artifacts:

- config: `frontend/playwright.config.ts`
- spec: `frontend/tests/e2e/full-stack.spec.ts`

The test starts:

- FastAPI on a dedicated backend port
- Next.js on a dedicated frontend port

Then it validates:

- homepage loads against the API-backed frontend
- skills search works
- skill detail pages render install metadata
- bundle pages render real bundle data
- docs center search/filter works across doc kinds
- docs pages render real skill docs
- teaching pages render real teaching markdown content
- project doc pages render real project markdown content
- doc detail pages can continue into related docs from the same front/back data flow
- doc detail pages expose context panels such as install entrypoints, learning-path position, and source metadata
- doc detail pages expose action panels with concrete repo commands, ordered runbook cues, expected-outcome hints, copy buttons, and next-step links

Run:

```text
npx playwright install chromium --prefix frontend
npm run build --prefix frontend
npm run e2e --prefix frontend
```

## Validation commands

Recommended minimum verification for this integration:

```text
python scripts/check_python_market_backend.py
python -m compileall backend
python scripts/check_docs_links.py
npm run build --prefix frontend
npm run e2e --prefix frontend
```

## Current status

This integration path is no longer just a plan.

It is now implemented as:

- a repo-backed Python API
- a dual-mode frontend data layer
- real bundle, docs, teaching, and project-doc pages
- a searchable docs-center explorer across all doc kinds
- shared related-doc navigation on detail pages
- shared context panels on detail pages
- shared action panels with ordered runbook cues, expected-outcome hints, and command-copy affordances on detail pages
- Playwright end-to-end coverage for the core market path
