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
- `POST /api/v1/local/skills/install`
- `POST /api/v1/local/bundles/install`
- `GET /api/v1/local/jobs/{job_id}`
- `GET /api/v1/docs/catalog`
- `GET /api/v1/docs/teaching/{doc_id}`
- `GET /api/v1/docs/project/{doc_id}`

The docs catalog now carries both grouped arrays and a flattened `all_docs` list so the frontend can filter across all doc families without reassembling the payload client-side.
That same shared payload now also supports detail-page related navigation, context panels, and copy-friendly ordered action panels with prerequisite, expected-outcome, and artifact/output cues without requiring separate recommendations or metadata endpoints.
Skill detail and bundle detail pages now also distinguish local CLI copy flows from future backend execution flows, so the current UI does not over-promise one-click installation.
The backend now also exposes the first mutation/job layer for local skill and bundle installs, while the frontend still keeps copy-first fallbacks until execution UI wiring is ready.

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
- screenshot capture: `frontend/tests/e2e/readme-screenshots.spec.ts`

The test starts:

- FastAPI on a dedicated backend port
- Next.js on a dedicated frontend port through `npm run dev:local`

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
- doc detail pages expose action panels with concrete repo commands, ordered runbook cues, prerequisite hints, expected-outcome hints, artifact/output hints, copy buttons, and next-step links
- skill detail pages show honest `Local CLI only` install messaging
- bundle detail pages expose bundle-level local `install-bundle`, `update-bundle`, and `remove-bundle` commands

Run:

```text
npx playwright install chromium --prefix frontend
npm run build --prefix frontend
npm run e2e --prefix frontend
npm run capture:readme-screenshots --prefix frontend
```

`npm run build` remains the production build check, while Playwright itself now starts the API-backed frontend in local dev mode so the suite is not blocked by environment-specific production server startup differences.

The screenshot capture flow writes repo-committable images to `docs/assets/readme/`, so the root README can show the current live market flow instead of hand-made mockups.

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
- shared action panels with ordered runbook cues, prerequisite hints, expected-outcome hints, artifact/output hints, and command-copy affordances on detail pages
- honest local install messaging on skill detail pages
- bundle-level local command panels on bundle detail pages
- backend local install job APIs for skill and bundle execution
- Playwright end-to-end coverage for the core market path

## Current gaps

The current front/back path is already good enough for repo-backed browsing and teaching, but it is not yet a full execution product.

What is already complete:

- browse/search/filter across skills, bundles, teaching docs, and project docs
- repo-backed detail pages
- command-copy, runbook, prerequisite, expected-outcome, and artifact hints
- honest local-command wording for skill install and bundle-level local actions
- backend local mutation APIs for first-pass skill and bundle install jobs
- end-to-end verification with Playwright

What is still partial:

- frontend buttons still copy local CLI commands instead of calling the new backend mutation APIs
- docs action panels are guidance-oriented and do not execute commands
- backend still does not expose update/remove/state mutation endpoints
- the current installer still expects a local install spec JSON file and does not fetch remote market artifacts over HTTP

The project roadmap for closing these gaps lives in [interaction-and-remote-install-roadmap.md](./interaction-and-remote-install-roadmap.md).
