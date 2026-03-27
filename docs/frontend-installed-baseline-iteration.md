# Frontend Installed Baseline Iteration

This iteration follows the completed installed-state doctor and low-risk repair pass.

## Goal

Expose the first installed-state baseline history surface in the frontend so local users can capture, review, and compare target-root snapshots without dropping back to raw CLI immediately.

## Scope

### 1. Add installed baseline summary to the frontend

- surface backend baseline-oriented snapshot metadata for a chosen target root
- show the latest baseline counts and health context directly in the UI
- keep skill and bundle detail pages scoped to the current target root

### 2. Add first baseline capture handoff

- expose a baseline capture action when the current target root is healthy or has already been reviewed
- keep the UI honest about what is archival versus what mutates the current runtime state
- preserve copy-first CLI fallbacks for advanced baseline and history workflows

### 3. Extend backend proxy coverage

- add Next.js proxy routes for baseline capture and baseline history
- keep the existing local lifecycle routing shape consistent with state, doctor, and repair

### 4. Extend Playwright

- verify one target root can capture a baseline from the frontend
- verify the baseline metadata updates in-page after capture
- verify the frontend distinguishes live state from archived baseline history clearly

## Acceptance criteria

- the frontend exposes a first baseline or baseline-history view/panel
- the frontend can trigger at least one baseline capture path through the backend
- README and integration docs explain the current baseline scope honestly
- Playwright covers at least one baseline capture flow

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-installed-baseline`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
