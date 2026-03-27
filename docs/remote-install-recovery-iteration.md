# Remote Install Recovery Iteration

This iteration follows the completed remote-install trust and approval pass.

## Goal

Add the first recovery and failure-handling layer to remote registry execution so frontend-triggered remote installs do not stop at "failed" with no next step.

## Scope

### 1. Surface recovery-oriented result states

- distinguish download failure, trust failure, installer failure, and user-cancel-safe states
- expose recovery hints next to remote execution summaries
- keep the current trust and approval surfaces visible while recovery is being added

### 2. Add first retry and cleanup actions

- allow the frontend to retry the last remote skill install from the same card
- allow the frontend to retry the last remote bundle install from the same card
- expose a cleanup/reset action for the staged cache or failed target root when the backend already has enough context

### 3. Preserve honest product boundaries

- do not imply full rollback if only retry and cleanup exist
- keep doctor, repair, baseline, and governance actions out of the remote execution cards for now
- keep copy-first CLI fallbacks visible for manual recovery

### 4. Extend Playwright to cover recovery

- verify a failed remote run shows a recovery hint
- verify retry becomes available after a failed remote run
- verify retry can succeed after the missing input or fixture problem is corrected

## Acceptance criteria

- remote execution failures show category-specific recovery guidance
- retry is available for the first failed remote skill and bundle flows
- README and integration docs explain the current recovery scope honestly
- Playwright covers at least one failed-then-retried remote install path

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-remote-install-recovery`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
