---
name: harness-engineering
description: Design skill-adjacent harnesses that coordinate routing, tools, state, evaluations, safety gates, and automation around agent workflows. Use when Codex needs to decide what belongs inside a skill versus in the surrounding harness, define tool contracts, add eval loops, design operational guardrails, or plan the future architecture of a skill-driven agent system.
---

# Harness Engineering

Use this skill to design the system layer around skills: routing, tool contracts, state, evals, safety gates, and automation.

## Safety First

- Treat automation, memory writes, and production tool execution as high-impact surfaces.
- Keep destructive or externally visible actions behind explicit confirmation or review gates.
- Do not confuse prompt conventions with enforced guarantees; move hard guarantees into the harness.
- Preserve clear human review points when designing irreversible flows.

## Task Router

- Define the core primitives of a harness and decide what belongs in the skill versus the outer system:
  Read [references/harness-primitives.md](./references/harness-primitives.md).
- Add evals, traces, regression loops, or review artifacts around a skill system:
  Read [references/evals-and-feedback.md](./references/evals-and-feedback.md).
- Design explicit tool contracts for skill scripts:
  Read [references/tool-contracts.md](./references/tool-contracts.md) and copy `assets/tool-contract-template.yaml`.
- Design publication or execution guardrails:
  Read [references/safety-gates.md](./references/safety-gates.md) and copy `assets/safety-gate-template.yaml`.
- Design automation specs around stable reporting workflows:
  Read [references/automation-patterns.md](./references/automation-patterns.md) and copy `assets/automation-spec-template.toml`.
- Plan how a skill ecosystem should evolve over time:
  Read [references/future-roadmap.md](./references/future-roadmap.md) and copy `assets/harness-blueprint.md`.
- Verify the bundled teaching resources for this skill:
  Run `python scripts/check_harness_engineering.py`.

## Progressive Loading

- Stay in this file for system boundaries, safety posture, and route selection.
- Read only the one `references/*.md` file that matches the current harness-design question.
- Load only `scripts/check_harness_engineering.py` when you need to execute or patch the local teaching checker.
- Open `assets/harness-blueprint.md` only when drafting a harness plan or review doc.
- Do not preload every harness reference just because this skill triggered.

## Default Workflow

1. Define the task family, success signal, and risk level.
2. Separate what the skill should teach from what the harness should enforce.
3. Specify tool contracts, state boundaries, review points, and default-off dangerous paths.
4. Add eval and feedback loops before adding more automation.
5. Stage rollout from manual to semi-automated to automated operation.
6. Revisit the skill surface after observing failures or drift in the harness.

## Reference Files

- [references/harness-primitives.md](./references/harness-primitives.md): core harness surfaces and the skill-versus-harness boundary.
- [references/evals-and-feedback.md](./references/evals-and-feedback.md): eval loops, traces, and regression strategy.
- [references/tool-contracts.md](./references/tool-contracts.md): how to turn skill scripts into explicit harness tools.
- [references/safety-gates.md](./references/safety-gates.md): how to block risky actions behind review and approval.
- [references/automation-patterns.md](./references/automation-patterns.md): how to specify repeatable automated runs safely.
- [references/future-roadmap.md](./references/future-roadmap.md): staged evolution from a static skill bundle to an operating harness.

## Bundled Resources

- `scripts/check_harness_engineering.py`: verifies this teaching skill ships the expected references and template sections.
- `assets/harness-blueprint.md`: copyable blueprint for sketching a skill-adjacent harness.
- `assets/tool-contract-template.yaml`: copyable scaffold for explicit tool contracts.
- `assets/safety-gate-template.yaml`: copyable scaffold for review and approval gates.
- `assets/automation-spec-template.toml`: copyable scaffold for automation plans.
