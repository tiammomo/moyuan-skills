# Frontend Interaction And Remote Install Roadmap

This roadmap tracks the remaining work required to turn the current repo-backed `skills market` browsing experience into a real installable product.

## Executive summary

Current status:

- frontend and backend browsing are already usable
- Playwright-covered detail flows already work
- command guidance in docs is already strong
- skill and bundle install entry points now use honest `local CLI only` language

The two biggest gaps are still:

1. many frontend buttons are guidance or command-copy affordances, not true execution flows
2. the installer still expects local install spec files and cannot directly pull a skill from a remote registry over HTTP

## Current-state assessment

### 1. Frontend / backend browsing

Status: `complete for read-only browsing`

Evidence:

- frontend pages already consume repo-backed backend APIs
- backend exposes market, bundle, and docs data through `GET` endpoints
- Playwright already covers homepage, skills, bundles, docs, and detail flows

What works well:

- skill search and filter
- skill detail display
- bundle detail display
- docs search and filter
- teaching, project, and skill doc detail pages

### 2. Frontend action buttons

Status: `partially complete`

What is already good:

- install commands are visible
- copy buttons work
- skill detail clearly states that install still means copying a local CLI command
- bundle detail now exposes first-class local bundle commands for `install-bundle`, `update-bundle`, and `remove-bundle`
- docs detail pages show ordered runbooks
- prerequisites, expected outcomes, and artifact hints are visible

What is still incomplete:

- skill install button still copies a local CLI command instead of executing install through the backend
- bundle detail actions are still local copy flows rather than backend-triggered execution
- docs action panels are still guidance widgets, not executable actions
- there is no frontend state for install progress, dry-run results, approval prompts, or failure recovery

### 3. Backend interaction layer

Status: `first pass implemented`

Current reality:

- backend now exposes:
  - `POST /api/v1/local/skills/install`
  - `POST /api/v1/local/bundles/install`
  - `GET /api/v1/local/jobs/{job_id}`
- the mutation layer reuses the existing local installer scripts
- long-running local operations now have a lightweight job model

What is still incomplete:

- there are no backend update/remove endpoints yet
- there is no installed-state read API for the UI
- the current frontend does not call the new mutation APIs yet

### 4. Remote skill pull / download

Status: `not implemented`

Current reality:

- `install_skill.py` installs from a local install spec path
- `skills_market.py install` forwards to the same local-file workflow
- there is no support for:
  - remote registry URL
  - skill id plus channel resolution from a remote host
  - HTTP download of install spec, package, or provenance
  - local cache management for downloaded artifacts

Short answer:

`not yet`

The project can install local packaged skills, but it still cannot fetch remote market artifacts directly.

## Buttons that are still not fully closed-loop

### Needs real backend execution

- skill detail install button
- bundle detail install, update, and remove actions
- future installed-state actions such as update, remove, doctor, and repair

### Already acceptable as non-execution UI

- navigation links
- search and filter controls
- docs related-navigation links
- command-copy buttons in docs

Those latter buttons are not unfinished. They are intentionally guidance-oriented.

## Recommended roadmap

### Phase 1: Make the frontend honest and complete for local execution

Goal:

- clearly separate `copy command` from `execute action`

Status:

- `complete for current local install surfaces`
- completed in this iteration:
  - the skill copy-install card now clearly says it only copies the local install command
  - bundle detail now includes first-class local commands for `install-bundle`, `update-bundle`, and `remove-bundle`
  - skill detail now keeps `Copy install command` visible while also offering `Run via backend`
  - bundle detail now keeps copy-first bundle commands visible while also offering backend bundle install execution
  - frontend now shows queued, running, succeeded, and failed states for local install jobs

Deliverables:

- rename existing install button UI so it is explicitly `Copy install command`
- add bundle-level command panels with `install-bundle`, `update-bundle`, and `remove-bundle`
- add UI states for:
  - pending
  - success
  - failed
  - requires manual approval

Acceptance criteria:

- no install-like button appears to be one-click if it still only copies text
- every install, update, or remove action in the UI has an honest label

### Phase 2: Add backend mutation APIs for local operations

Goal:

- let frontend trigger local market actions through FastAPI

Status:

- `in progress`
- completed in this iteration:
  - `POST /api/v1/local/skills/install`
  - `POST /api/v1/local/bundles/install`
  - `GET /api/v1/local/jobs/{job_id}`
  - backend smoke coverage for local install jobs
  - Next.js local proxy routes now forward skill and bundle install requests to the FastAPI backend
  - skill detail pages can trigger local skill install jobs and show job progress in the UI
  - bundle detail pages can trigger local bundle install jobs and show job progress in the UI

Suggested endpoints:

- `POST /api/v1/local/skills/install`
- `POST /api/v1/local/skills/update`
- `POST /api/v1/local/skills/remove`
- `POST /api/v1/local/bundles/install`
- `POST /api/v1/local/bundles/update`
- `POST /api/v1/local/bundles/remove`
- `POST /api/v1/local/state/doctor`
- `GET /api/v1/local/jobs/{job_id}`
- `GET /api/v1/local/state`

Design notes:

- do not block the request until install finishes
- model these operations as jobs with progress, artifacts, and summary
- reuse the existing Python scripts under `scripts/` rather than rewriting logic

Acceptance criteria:

- frontend can install, update, and remove a local skill through backend APIs
- job progress and final summary are visible in the UI

Remaining work before Phase 2 can be called complete:

- add local update/remove/state endpoints

### Phase 3: Add remote registry fetch and remote install

Goal:

- install a skill without needing a preexisting local install spec file

Suggested CLI shape:

```text
python scripts/skills_market.py install moyuan.release-note-writer --registry https://example.com/registry
python scripts/skills_market.py install-bundle release-engineering-starter --registry https://example.com/registry
```

Required capabilities:

- fetch channel index or skill metadata over HTTP
- resolve install spec from remote registry
- download package artifact
- download provenance artifact
- verify checksum and provenance before install
- cache downloaded artifacts locally

Acceptance criteria:

- a user can install by skill id or bundle id plus registry URL
- the local installer no longer depends on a manually prepared local install spec

### Phase 4: Add trust, approval, and recovery flows

Goal:

- make remote install safe enough for repeated use

Deliverables:

- approval prompt before shell, network, or high-risk install
- publisher trust signal in frontend install dialog
- provenance verification summary in install results
- retry, rollback, and remove-on-failure flows
- explicit lifecycle handling for deprecated, blocked, or archived skills

Acceptance criteria:

- risky installs are never silent
- failed installs leave a clear recovery path

### Phase 5: Add installed-state product surfaces

Goal:

- expose the already-built local client lifecycle to the UI

Deliverables:

- installed skills page
- installed bundles page
- doctor and repair action pages
- baseline history page
- waiver, gate, and audit summary page

Acceptance criteria:

- the frontend becomes a real local client surface, not only a browse-and-docs surface

## Priority recommendation

Recommended execution order:

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5

Why:

- first make the UI honest
- then make local execution possible
- then add remote install
- then harden it with trust and approval
- then expose deeper lifecycle and governance surfaces

## Short answer for project status

If you need a simple conclusion:

- `frontend/backend interaction` is already strong for browsing and teaching
- `frontend execution` is now working for local skill and bundle installs, but not yet for update/remove/state workflows
- `remote skill download and install` is not yet supported

The next implementation target is now the remaining backend side of `Phase 2`: local update/remove/state endpoints that can support fuller installed-state product surfaces.
