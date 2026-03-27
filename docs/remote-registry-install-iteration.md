# Remote Registry Install Iteration

This iteration follows the completed backend local lifecycle API pass.

## Goal

Start the first real remote install path so a user can resolve a skill or bundle from a hosted registry instead of relying on a pre-generated local install spec file.

## Scope

### 1. Add remote registry lookup for skill install

- accept a registry base URL together with a skill id or skill name
- fetch remote index or detail metadata over HTTP
- resolve the remote install spec before handing off to the existing installer
- keep local install behavior unchanged when no registry URL is provided

### 2. Add remote registry lookup for bundle install

- accept a registry base URL together with a bundle id
- fetch remote bundle metadata and the required install specs
- preserve the current local bundle workflow as the fallback mode

### 3. Introduce downloaded artifact staging

- download remote install specs and package artifacts into a deterministic cache/staging location
- record where the remote artifacts were sourced from
- keep the first pass focused on checksum verification and clear provenance hooks

### 4. Keep trust and approval boundaries explicit

- do not silently bypass existing provenance or publisher checks
- do not imply that remote install is fully hardened until the next trust-focused iteration
- return clear error messages when registry fetch, download, or checksum validation fails

## Acceptance criteria

- a skill can be installed by `skill id + registry URL`
- a bundle can be installed by `bundle id + registry URL`
- downloaded install specs and package artifacts are staged locally before install
- docs and roadmap clearly distinguish local lifecycle APIs from remote download support

## Validation plan

- `python scripts/check_python_market_backend.py`
- `python scripts/check_market_pipeline.py --output-root dist/market-smoke-remote-registry-install`
- `python scripts/check_docs_links.py`
- `npm run build --prefix frontend`
- `npm run e2e --prefix frontend`
