---
name: release-note-writer
description: Draft and lint structured product or project release notes from a JSON change feed, using a reusable template and review rules. Use when Codex needs to turn structured changes into release announcements, prepare internal or external release summaries, validate a release-note draft before publishing, or extend a practical example business skill with references, scripts, assets, and checks.
---

# Release Note Writer

Use this skill to turn a structured change feed into a publication-ready release-note draft, then lint the draft before human review.

## Safety First

- Treat release notes as externally visible communication unless the user says they are internal-only.
- Do not invent product commitments, dates, or user impact that are not present in the source changes.
- Keep security-sensitive issues, customer names, or confidential roadmap details out of public notes unless they are explicitly approved.
- Always lint or manually review a generated draft before publishing.

## Task Router

- Draft a release note from structured input:
  Use `python scripts/release_note_writer.py draft <input.json> <output.md>`, then read [references/input-contract.md](./references/input-contract.md).
- Improve tone, structure, or audience fit for a release note:
  Read [references/writing-rules.md](./references/writing-rules.md).
- Review a draft before publishing:
  Read [references/review-checklist.md](./references/review-checklist.md), then run `python scripts/release_note_writer.py lint <draft.md>`.
- Verify or extend this bundled skill example:
  Run `python scripts/check_release_note_writer.py`.

## Progressive Loading

- Stay in this file for routing, safety rules, and command selection.
- Read only the one `references/*.md` file that matches the current authoring or review task.
- Load only `scripts/release_note_writer.py` or `scripts/check_release_note_writer.py` when you need to execute, debug, or patch the implementation.
- Open `assets/release-note-template.md` or `assets/sample-release-input.json` only when generating or reviewing concrete output.
- Do not preload every reference file just because this skill triggered.

## Default Workflow

1. Confirm the audience, release version, and source-of-truth change feed.
2. Draft the release notes from structured JSON input and the bundled template.
3. Review the generated summary, highlights, and grouped change sections.
4. Run the draft through the bundled linter.
5. Apply any audience-specific edits only after the factual content is stable.
6. Keep final human review before publication for externally visible notes.

## Reference Files

- [references/input-contract.md](./references/input-contract.md): JSON input contract, field meanings, and grouping behavior.
- [references/writing-rules.md](./references/writing-rules.md): editorial rules for summary quality, highlights, and audience fit.
- [references/review-checklist.md](./references/review-checklist.md): pre-publish review checklist and common risks.

## Bundled Resources

- `scripts/release_note_writer.py`: deterministic CLI that drafts or lints release notes.
- `scripts/check_release_note_writer.py`: local smoke checker that drafts and lints a sample release note.
- `assets/release-note-template.md`: reusable markdown template for generated notes.
- `assets/sample-release-input.json`: example structured change feed for local testing and teaching.

