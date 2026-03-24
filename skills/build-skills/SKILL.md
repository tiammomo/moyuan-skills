---
name: build-skills
description: Teach how to design, scaffold, validate, and evolve reusable Codex skills with clear routing and bundled resources. Use when Codex needs to create a new skill, refactor an existing skill, tighten triggers, decide what belongs in SKILL.md versus references/scripts/assets, or add a maintainable validation loop around a skill.
---

# Build Skills

Use this skill to turn a fuzzy requirement into a reusable skill with narrow triggers, clear routing, and a validation path that can survive future edits.

## Safety First

- Keep secrets, internal URLs, and live credentials out of examples, references, and assets.
- Do not create `scripts/`, `references/`, or `assets/` just for symmetry; add them only when they earn their keep.
- Keep irreversible or high-risk actions behind explicit confirmation when designing a skill workflow.
- Prefer the smallest working skill before adding more structure.

## Task Router

- Design a brand-new skill from scratch:
  Read [references/design-flow.md](./references/design-flow.md) and copy the template in `assets/skill-design-canvas.md`.
- Decide what belongs in the core skill file, reference files, scripts, or assets:
  Read [references/resource-planning.md](./references/resource-planning.md).
- Add skill-local checks, smoke tests, and iteration loops:
  Read [references/validation-loop.md](./references/validation-loop.md), then run `python scripts/check_build_skills.py` if you want to verify this teaching bundle.
- Review an existing skill for trigger quality, routing clarity, or bloat:
  Read [references/design-flow.md](./references/design-flow.md), then switch to the file-placement route above if the problem turns into a packaging question.

## Progressive Loading

- Stay in this file for routing, safety, and workflow selection.
- Read only the one `references/*.md` file that matches the current authoring problem.
- Load only `scripts/check_build_skills.py` when you need to execute or patch the local teaching checker.
- Open `assets/skill-design-canvas.md` only when you need a copyable design brief.
- Do not preload every reference file just because this skill triggered.

## Default Workflow

1. Collect a small set of realistic user requests that should trigger the skill.
2. Draft the frontmatter description before writing the rest of the skill.
3. Split content across `SKILL.md`, `references/`, `scripts/`, and `assets/`.
4. Add the smallest useful reference or script that reduces repeated work.
5. Add a local validation path before expanding scope.
6. Revisit what should stay in the skill versus what should eventually move into a harness.

## Reference Files

- [references/design-flow.md](./references/design-flow.md): end-to-end design flow from user requests to a skill skeleton.
- [references/resource-planning.md](./references/resource-planning.md): rules for placing content in `SKILL.md`, `references/`, `scripts/`, or `assets/`.
- [references/validation-loop.md](./references/validation-loop.md): local checks, forward-testing ideas, and iteration triggers.

## Bundled Resources

- `scripts/check_build_skills.py`: verifies this teaching skill ships the expected references and template sections.
- `assets/skill-design-canvas.md`: copyable design canvas for planning a new or refactored skill.
