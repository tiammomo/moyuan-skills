---
name: issue-triage-report
description: Draft and lint a structured issue triage report from CSV issue exports, grouping urgent issues, decision blockers, assigned follow-ups, and backlog watch items. Use when Codex needs to turn issue tracker exports into a weekly triage summary, prepare an engineering or product operations review, validate a triage report before circulation, or extend a practical business skill with CSV parsing, references, templates, and checks.
---

# Issue Triage Report

Use this skill to turn a CSV issue export into a concise triage report for engineering, product, or operations review.

## Safety First

- Treat customer-impact notes, security items, and unreleased work as potentially sensitive.
- Do not invent owners, status, or mitigation steps that are not present in the source CSV.
- Keep customer names or incident details out of broad-circulation reports unless they are explicitly approved.
- Review the generated report before sharing it outside the immediate working group.

## Task Router

- Draft a triage report from a CSV issue export:
  Use `python scripts/issue_triage_report.py draft <input.csv> <output.md>`, then read [references/input-contract.md](./references/input-contract.md).
- Improve grouping, wording, or the intended audience of a triage report:
  Read [references/writing-rules.md](./references/writing-rules.md).
- Review a triage report before circulation:
  Read [references/review-checklist.md](./references/review-checklist.md), then run `python scripts/issue_triage_report.py lint <draft.md>`.
- Verify or extend this bundled skill example:
  Run `python scripts/check_issue_triage_report.py`.

## Progressive Loading

- Stay in this file for routing, safety rules, and command selection.
- Read only the single `references/*.md` file that matches the current drafting or review task.
- Load only `scripts/issue_triage_report.py` or `scripts/check_issue_triage_report.py` when you need to execute, debug, or patch the implementation.
- Open `assets/issue-triage-template.md` or `assets/sample-issues.csv` only when generating or reviewing concrete output.
- Do not preload every reference file just because this skill triggered.

## Default Workflow

1. Confirm the audience and the source-of-truth CSV export.
2. Draft the triage report from the input CSV and bundled template.
3. Review the urgent issues, decision blockers, assigned follow-ups, and backlog watch sections.
4. Run the generated draft through the bundled linter.
5. Adjust audience-specific wording only after the grouped facts are correct.
6. Keep a human review step before sending the report to a wider audience.

## Reference Files

- [references/input-contract.md](./references/input-contract.md): CSV columns, allowed values, and grouping rules.
- [references/writing-rules.md](./references/writing-rules.md): editorial guidance for triage summaries and section quality.
- [references/review-checklist.md](./references/review-checklist.md): pre-circulation review checklist and common pitfalls.

## Bundled Resources

- `scripts/issue_triage_report.py`: deterministic CLI that drafts or lints issue triage reports.
- `scripts/check_issue_triage_report.py`: local smoke checker that drafts and lints a sample triage report.
- `assets/issue-triage-template.md`: reusable markdown template for generated triage reports.
- `assets/sample-issues.csv`: sample CSV issue export for testing and teaching.

