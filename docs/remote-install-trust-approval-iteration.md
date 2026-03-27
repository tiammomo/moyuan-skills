# Remote Install Trust And Approval Iteration

This iteration follows the completed frontend installed-state UI pass.

## Goal

Add the first trust and approval layer to remote registry execution so frontend-triggered remote installs stop looking like unconditional fire-and-forget jobs.

## Scope

### 1. Add remote install trust summary surfaces

- expose publisher, review status, lifecycle status, and provenance hints next to the remote execution cards
- show when a remote install is coming from a verified publisher profile
- show whether the requested skill or bundle is deprecated, blocked, or archived before execution starts

### 2. Add explicit approval inputs for remote execution

- require an explicit confirmation step before a remote install job is submitted
- keep the approval UX scoped to frontend-triggered remote skill install and remote bundle install
- make the approval state visible in-page so the user can tell “not approved yet” from “backend unavailable”

### 3. Keep the current execution split honest

- preserve copy-first local commands
- preserve installed-state lifecycle cards for local update/remove
- avoid implying that rollback, retry, or full policy gating is already productized in the frontend

### 4. Extend Playwright to cover the trust/approval flow

- verify the remote execution buttons stay blocked until approval is given
- verify one remote skill install after approval
- verify one remote bundle install after approval

## Acceptance criteria

- remote execution cards show trust-oriented metadata before execution
- remote execution requires explicit approval before the job is submitted
- README and integration docs clearly explain the new trust/approval behavior
- Playwright covers the approval gate and the post-approval execution path

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-remote-install-trust-approval`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
