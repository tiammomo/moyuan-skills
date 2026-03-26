# Market Installed History Waiver Remediation Iteration

This temporary note tracks the next installed-state history waiver-remediation iteration for the local skills market client.

## Goals

- [x] Add remediation guidance for expired, unmatched, or stale installed baseline history waivers
- [x] Wire the remediation workflow into the unified CLI, docs, and smoke pipeline
- [x] Run validation, then delete this note after the iteration is fully complete

## Current Status

- Completed in this iteration:
  - Added `scripts/remediate_installed_baseline_history_waivers.py` and the `python scripts/skills_market.py remediate-installed-history-waivers ...` CLI workflow.
  - Synced the remediation workflow into the root README, consumer docs, governance docs, registry docs, repo command guide, and teaching materials.
  - Extended the market smoke pipeline to cover healthy remediation output, strict remediation failures, and post-prune remediation guidance.
- Validation passed before cleanup:
  - `python scripts/check_progressive_skills.py`
  - `python scripts/check_docs_links.py`
  - `python scripts/check_harness_prototypes.py`
  - `python scripts/check_market_governance.py`
  - `python scripts/validate_market_manifest.py`
  - 7 skill checkers
  - `python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json`
  - `python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml`
  - `python scripts/check_market_pipeline.py --output-root dist/market-smoke-installed-history-waiver-remediation-iteration`
