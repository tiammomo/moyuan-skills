---
name: progressive-disclosure
description: Design layered loading strategies for reusable skills so metadata, routing, references, scripts, assets, and harness concerns stay in the right place. Use when Codex needs to refactor a bloated skill, plan on-demand references, reduce context cost, choose what belongs in each layer, or turn a monolithic instruction set into a progressive skill.
---

# Progressive Disclosure

Use this skill to decide how a capability should be split across trigger metadata, `SKILL.md`, references, scripts, assets, and future harness layers.

## Safety First

- Do not hide essential safety rules in deep reference files.
- Do not split content so aggressively that the router becomes a maze.
- Keep reference routing within one or two hops from `SKILL.md`.
- Optimize for clarity first, then token efficiency.

## Task Router

- Decide what belongs in frontmatter, the core skill file, reference files, scripts, assets, or a future harness:
  Read [references/loading-splits.md](./references/loading-splits.md).
- Improve `Task Router` wording, reference topology, or long-file navigation:
  Read [references/routing-patterns.md](./references/routing-patterns.md).
- Refactor a monolithic skill into a layered structure:
  Read [references/refactor-playbook.md](./references/refactor-playbook.md) and copy `assets/loading-plan-template.md`.
- Verify the bundled teaching resources for this skill:
  Run `python scripts/check_progressive_disclosure.py`.

## Progressive Loading

- Stay in this file for safety rules, layer selection, and router choice.
- Read only the single `references/*.md` file that matches the current layering problem.
- Load only `scripts/check_progressive_disclosure.py` when you need a local smoke check or want to patch the teaching bundle.
- Open `assets/loading-plan-template.md` only when drafting or reviewing a refactor plan.
- Do not preload every reference file just because this skill triggered.

## Default Workflow

1. Inspect the current skill or instruction bundle and list its major task branches.
2. Decide what must stay visible at trigger time versus only after routing.
3. Move topic depth into references and repeated execution into scripts.
4. Add or tighten router entries so each task has a narrow entry point.
5. Re-run structure checks after refactoring.
6. Revisit what now belongs in a future harness instead of the skill itself.

## Reference Files

- [references/loading-splits.md](./references/loading-splits.md): decide what belongs in each layer.
- [references/routing-patterns.md](./references/routing-patterns.md): write better routers and keep references reachable.
- [references/refactor-playbook.md](./references/refactor-playbook.md): practical sequence for shrinking an overgrown skill.

## Bundled Resources

- `scripts/check_progressive_disclosure.py`: verifies this teaching skill ships the expected references and template sections.
- `assets/loading-plan-template.md`: copyable worksheet for planning a progressive-disclosure refactor.
