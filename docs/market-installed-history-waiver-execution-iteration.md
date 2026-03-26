# Market Installed History Waiver Execution Iteration

This temporary note tracks the next installed-state history waiver-execution iteration for the local skills market client.

## Goals

- [x] Turn remediation guidance into repeatable execution helpers for renewal, cleanup, or replacement work
- [x] Expose the execution workflow through the unified CLI, documentation, and smoke pipeline
- [x] Run validation, then delete this note after the iteration is fully complete

## Current Status

- Completed in this iteration:
  - Added `scripts/draft_installed_baseline_history_waiver_execution.py` and the `python scripts/skills_market.py draft-installed-history-waiver-execution ...` workflow.
  - Generated safe execution packs that turn remediation results into renewal drafts, replacement drafts, or cleanup-review artifacts without mutating governance source files.
  - Synced the workflow into the root README, consumer docs, governance docs, registry docs, repo command guide, and teaching materials.
  - Extended the market smoke pipeline to cover healthy execution drafting, failing draft generation, and post-prune cleanup-review fallback.
- Validation passed before cleanup:
  - `python scripts/check_progressive_skills.py`
  - `python scripts/check_docs_links.py`
  - `python scripts/check_harness_prototypes.py`
  - `python scripts/check_market_governance.py`
  - `python scripts/validate_market_manifest.py`
  - 7 skill checkers
  - `python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json`
  - `python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml`
  - `python scripts/check_market_pipeline.py --output-root dist/market-smoke-installed-history-waiver-execution-release`
