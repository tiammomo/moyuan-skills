# Market Installed History Waiver Apply Iteration

This temporary note tracks the next installed-state history waiver-apply iteration for the local skills market client.

## Goals

- [x] Turn reviewed waiver preview artifacts into safe apply-ready patch outputs for governance source files
- [x] Expose the apply workflow through the unified CLI, documentation, and smoke pipeline
- [x] Run validation, then delete this note after the iteration is fully complete

## Current Status

- Completed in this iteration:
  - Added `scripts/prepare_installed_baseline_history_waiver_apply.py` and the `python scripts/skills_market.py prepare-installed-history-waiver-apply ...` workflow.
  - Generated safe apply-ready artifacts from waiver previews, including per-waiver target candidates, per-waiver patch files, and a combined patch bundle.
  - Covered both update patches and delete patches for review-only cleanup cases without mutating governance source files.
  - Synced the apply workflow into the root README, consumer docs, governance docs, registry docs, repo command guide, and teaching materials.
  - Extended the market smoke pipeline to cover healthy apply output, failing update patches, and post-prune delete-patch fallback.
- Validation passed before cleanup:
  - `python scripts/check_progressive_skills.py`
  - `python scripts/check_docs_links.py`
  - `python scripts/check_harness_prototypes.py`
  - `python scripts/check_market_governance.py`
  - `python scripts/validate_market_manifest.py`
  - 7 skill checkers
  - `python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json`
  - `python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml`
  - `python scripts/check_market_pipeline.py --output-root dist/market-smoke-installed-history-waiver-apply-release`
