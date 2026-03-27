# Frontend Remote Execution UI Iteration

This iteration follows the completed remote registry install pass.

## Goal

Expose the new backend remote registry install APIs through the existing frontend skill and bundle detail pages.

## Scope

### 1. Add remote execution UI for skill detail

- allow the user to provide a registry URL
- trigger `POST /api/v1/registry/skills/install`
- reuse the current job polling UI so local and remote runs feel consistent

### 2. Add remote execution UI for bundle detail

- allow the user to provide a registry URL for starter bundles
- trigger `POST /api/v1/registry/bundles/install`
- keep copy-first CLI fallbacks visible

### 3. Keep local and remote modes clearly separated

- preserve the current `Copy install command` and local backend execution cards
- label remote execution explicitly as registry-backed
- avoid implying that remote install trust/approval hardening is already complete

### 4. Extend Playwright to cover remote execution

- stand up a temporary hosted registry during E2E
- verify one remote skill install flow
- verify one remote bundle install flow

## Acceptance criteria

- skill detail can launch a remote registry install job from the UI
- bundle detail can launch a remote registry install job from the UI
- job status and result summaries are visible in-page
- docs and README clearly distinguish local execution from remote execution

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-remote-execution-ui`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
