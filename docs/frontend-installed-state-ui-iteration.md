# Frontend Installed-State UI Iteration

This iteration follows the completed frontend remote execution pass.

## Goal

Expose the backend local lifecycle state APIs through the frontend so the market stops at less copy-first lifecycle guidance and starts showing the real installed state.

## Scope

### 1. Add installed-state read surfaces

- proxy `GET /api/v1/local/state`
- show whether the current skill or bundle is already installed under the default frontend target root
- expose installed counts and lightweight ownership summary in-page

### 2. Add first update and remove execution UI

- trigger `POST /api/v1/local/skills/update`
- trigger `POST /api/v1/local/skills/remove`
- trigger `POST /api/v1/local/bundles/update`
- trigger `POST /api/v1/local/bundles/remove`
- reuse the existing job polling card pattern so install/update/remove all feel consistent

### 3. Keep copy-first guidance visible

- preserve the current copyable CLI commands
- label lifecycle actions honestly so users can tell read-only guidance from executable actions
- avoid implying that doctor / repair / baseline governance pages are already productized

### 4. Extend Playwright to cover lifecycle transitions

- verify one skill update or remove flow after install
- verify one bundle update or remove flow after install
- assert that the frontend reflects installed-state changes rather than only terminal output

## Acceptance criteria

- the frontend can read installed-state data from the backend
- skill and bundle detail pages can launch update/remove jobs from the UI
- job progress and final summaries are visible in-page
- README and docs clearly describe which installed-state actions are now executable

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-installed-state-ui`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
