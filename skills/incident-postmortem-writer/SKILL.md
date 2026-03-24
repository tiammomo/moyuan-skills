---
name: incident-postmortem-writer
description: Draft and lint structured incident postmortems from a JSON incident record, including impact, timeline, root cause, and action items with publication guardrails. Use when Codex needs to turn incident metadata into an internal postmortem draft, prepare a reviewable incident summary, validate a postmortem before circulation, or extend a realistic business skill with stronger safety, structured timelines, and action-item reporting.
---

# Incident Postmortem Writer

Use this skill to turn a structured incident record into a reviewable postmortem draft with explicit impact, timeline, root cause, and action items.

## Safety First

- Treat incident records as sensitive by default, especially for customer impact, security detail, and operator error.
- Do not publish raw internal investigation notes or unapproved blame-oriented language.
- Keep customer names, exact exploit details, and internal-only infrastructure references out of broadly circulated drafts unless explicitly approved.
- Always require human review before circulation outside the incident response group.

## Task Router

- Draft a postmortem from a structured incident JSON file:
  Use `python scripts/incident_postmortem_writer.py draft <input.json> <output.md>`, then read [references/input-contract.md](./references/input-contract.md).
- Improve tone, guardrails, or post-incident communication quality:
  Read [references/communication-guardrails.md](./references/communication-guardrails.md).
- Review a draft before circulation:
  Read [references/review-checklist.md](./references/review-checklist.md), then run `python scripts/incident_postmortem_writer.py lint <draft.md>`.
- Verify or extend this bundled skill example:
  Run `python scripts/check_incident_postmortem_writer.py`.

## Progressive Loading

- Stay in this file for routing, safety rules, and command selection.
- Read only the one `references/*.md` file that matches the current drafting or review task.
- Load only `scripts/incident_postmortem_writer.py` or `scripts/check_incident_postmortem_writer.py` when you need to execute, debug, or patch the implementation.
- Open `assets/postmortem-template.md` or `assets/sample-incident.json` only when generating or reviewing concrete output.
- Do not preload every reference file just because this skill triggered.

## Default Workflow

1. Confirm the audience and the source-of-truth incident record.
2. Draft the postmortem from the structured incident JSON and bundled template.
3. Review the impact statement, timeline fidelity, root cause wording, and action items.
4. Run the draft through the bundled linter.
5. Remove or generalize sensitive detail before broader circulation.
6. Keep a human review and approval step before publication.

## Reference Files

- [references/input-contract.md](./references/input-contract.md): required incident fields, timeline structure, and action-item format.
- [references/communication-guardrails.md](./references/communication-guardrails.md): tone, blame avoidance, and sensitive-content guardrails.
- [references/review-checklist.md](./references/review-checklist.md): pre-circulation review checklist and postmortem risks.

## Bundled Resources

- `scripts/incident_postmortem_writer.py`: deterministic CLI that drafts or lints incident postmortems.
- `scripts/check_incident_postmortem_writer.py`: local smoke checker that drafts and lints a sample postmortem.
- `assets/postmortem-template.md`: reusable markdown template for generated postmortems.
- `assets/sample-incident.json`: sample structured incident record for testing and teaching.

