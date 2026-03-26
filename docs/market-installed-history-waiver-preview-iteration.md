# Market Installed History Waiver Preview Iteration

This temporary note tracks the next installed-state history waiver-preview iteration for the local skills market client.

## Goals

- [x] Compare generated waiver execution drafts against source waiver files and surface review-friendly previews
- [x] Expose the preview workflow through the unified CLI, documentation, and smoke pipeline
- [x] Run validation, then delete this note after the iteration is fully complete

## Current Status

- Completed in this iteration:
  - Added `scripts/preview_installed_baseline_history_waiver_execution.py` and the `python scripts/skills_market.py preview-installed-history-waiver-execution ...` workflow.
  - Compared source waiver files against generated renewal/replacement drafts and surfaced review-friendly changed-field previews.
  - Added cleanup-review previews for cases where preview should stay review-only instead of forcing a draft update.
  - Synced the preview workflow into the root README, consumer docs, governance docs, registry docs, repo command guide, and teaching materials.
  - Extended the market smoke pipeline to cover healthy preview output, failing draft previews, and post-prune cleanup-preview fallback.
- Validation passed before cleanup:
  - `python scripts/check_progressive_skills.py`
  - `python scripts/check_docs_links.py`
  - `python scripts/check_harness_prototypes.py`
  - `python scripts/check_market_governance.py`
  - `python scripts/validate_market_manifest.py`
  - 7 skill checkers
  - `python scripts/run_eval_harness.py --baseline examples/eval-harness/baseline.json`
  - `python scripts/run_harness_runtime.py examples/harness-prototypes/runtime-blueprints/release-note-publication.yaml`
  - `python scripts/check_market_pipeline.py --output-root dist/market-smoke-installed-history-waiver-preview-release`
