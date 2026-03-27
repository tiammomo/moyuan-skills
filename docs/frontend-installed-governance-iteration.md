# Frontend Installed Governance Iteration

This iteration follows the completed installed-state baseline history pass.

## Goal

Expose the first installed-state governance summary surface in the frontend so local users can review waiver, gate, and audit context for a target root without dropping back to raw CLI immediately.

## Scope

### 1. Add installed governance summary to the frontend

- surface backend governance-oriented summary metadata for a chosen target root
- show current waiver, gate, and audit counts directly in the UI
- keep skill and bundle detail pages scoped to the current target root

### 2. Add first governance handoff

- expose at least one governance-oriented read or refresh action from the frontend
- keep the UI honest about what is review-only versus what mutates governance state
- preserve copy-first CLI fallbacks for advanced waiver and gate workflows

### 3. Extend backend proxy coverage

- add Next.js proxy routes for governance summary reads and the first governance refresh flow
- keep the existing local lifecycle routing shape consistent with state, doctor, repair, and baseline

### 4. Extend Playwright

- verify one target root can read governance context from the frontend
- verify the governance summary updates in-page after the first supported refresh path
- verify the frontend distinguishes installed-state health from governance review state clearly

## Acceptance criteria

- the frontend exposes a first governance view or panel
- the frontend can trigger at least one governance-oriented backend flow
- README and integration docs explain the current governance scope honestly
- Playwright covers at least one governance summary flow

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-installed-governance`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
