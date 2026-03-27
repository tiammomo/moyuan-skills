# Frontend Installed Waiver Apply Iteration

This iteration follows the completed installed-state governance summary pass.

## Goal

Expose the first waiver-review and apply-handoff surface in the frontend so local users can move from governance summary into concrete waiver follow-up without immediately dropping back to raw CLI for every step.

## Scope

### 1. Add waiver review context to the frontend

- surface the latest waiver-focused follow-up actions from the governance summary artifacts
- distinguish read-only waiver review from write-capable apply execution clearly
- keep skill and bundle detail pages scoped to the active target root

### 2. Add first apply-handoff action

- expose at least one waiver/apply-oriented refresh or prepare action from the frontend
- keep the UI explicit about what still remains copy-first or manually reviewed
- preserve CLI follow-ups for write-mode apply execution and rollback-heavy flows

### 3. Extend backend proxy coverage

- add Next.js proxy routes for the first waiver/apply-oriented backend refresh path
- keep the lifecycle routing shape consistent with state, doctor, repair, baseline, and governance

### 4. Extend Playwright

- verify one target root can read waiver/apply context from the frontend
- verify the first supported waiver/apply refresh path updates in-page
- verify the frontend still separates governance review from write-oriented apply execution

## Acceptance criteria

- the frontend exposes a first waiver/apply view or panel
- the frontend can trigger at least one waiver/apply-oriented backend flow
- README and integration docs explain the current waiver/apply scope honestly
- Playwright covers at least one waiver/apply summary flow

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-frontend-installed-waiver-apply`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
