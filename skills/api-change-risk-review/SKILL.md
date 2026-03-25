---
name: api-change-risk-review
description: Compute diffs, draft reviews, and lint API change risk reports from before/after schema snapshots or a precomputed diff JSON. Use when Codex needs to review API evolution, prepare an engineering or platform review, assess rollout risk for interface changes, or teach a tool-heavy business skill with multi-step scripts, references, assets, and checks.
---

# API Change Risk Review

Use this skill to turn API schema changes into a reviewable risk report with explicit breaking changes, migration notes, rollout checks, and open questions.

## Safety First

- Treat API compatibility reviews as release gates, not as optional editorial output.
- Do not invent rollout guarantees, compatibility claims, or migration safety that are not supported by the diff.
- Flag security, auth, or data-contract changes clearly before broader rollout.
- Keep final approval with the owning API or platform team before publishing the review.

## Task Router

- Compute a diff from before/after schema snapshots:
  Use `python scripts/api_change_risk_review.py diff <before.json> <after.json> <diff.json>`, then read [references/input-contract.md](./references/input-contract.md).
- Draft a risk review from a structured API diff:
  Use `python scripts/api_change_risk_review.py draft <diff.json> <output.md>`, then read [references/risk-rules.md](./references/risk-rules.md).
- Review a draft before rollout or circulation:
  Read [references/review-checklist.md](./references/review-checklist.md), then run `python scripts/api_change_risk_review.py lint <draft.md>`.
- Verify or extend this bundled skill example:
  Run `python scripts/check_api_change_risk_review.py`.

## Progressive Loading

- Stay in this file for routing, safety rules, and command selection.
- Read only the single `references/*.md` file that matches the current diffing, drafting, or review task.
- Load only `scripts/api_change_risk_review.py` or `scripts/check_api_change_risk_review.py` when you need to execute, debug, or patch the implementation.
- Open `assets/api-change-risk-template.md`, `assets/sample-before.json`, or `assets/sample-after.json` only when generating or reviewing a concrete example.
- Do not preload every reference file just because this skill triggered.

## Default Workflow

1. Confirm the source-of-truth before/after schema snapshots and intended audience.
2. Run the deterministic diff step before drafting any human-facing review.
3. Draft the risk review from the diff and bundled template.
4. Review the breaking changes, migration notes, rollout checks, and open questions.
5. Run the bundled linter before circulation.
6. Keep final approval with the owning API or platform team before rollout.

## Reference Files

- [references/input-contract.md](./references/input-contract.md): before/after schema format and generated diff structure.
- [references/risk-rules.md](./references/risk-rules.md): how to assess change severity, rollout risk, and migration quality.
- [references/review-checklist.md](./references/review-checklist.md): pre-rollout review checklist and approval questions.

## Bundled Resources

- `scripts/api_change_risk_review.py`: deterministic CLI that diffs schema snapshots, drafts risk reviews, and lints the result.
- `scripts/check_api_change_risk_review.py`: local smoke checker that runs diff, draft, and lint over the bundled example.
- `assets/api-change-risk-template.md`: reusable markdown template for generated API risk reviews.
- `assets/sample-before.json`: sample API schema snapshot before a release.
- `assets/sample-after.json`: sample API schema snapshot after a release.
