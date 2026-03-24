# Layer Split Rules

## Frontmatter

Keep only trigger-critical information in frontmatter:

- what the skill does
- when the skill should trigger

If it is not needed for triggering, it probably should not live here.

## SKILL.md

Use `SKILL.md` for the first decision after trigger time:

- what is safe
- which branch to take
- what the default workflow is

If the agent only needs the detail after choosing a branch, move that detail out.

## references/

Use `references/` for topic depth:

- API rules
- domain policy
- special-case workflows
- troubleshooting

Reference files should be readable on demand without changing the main router.

## scripts/

Use `scripts/` when the work is better executed than described:

- fragile command sequences
- deterministic transformations
- local validation helpers

Scripts reduce repeated reasoning when the desired behavior is stable.

## assets/

Use `assets/` for output-facing resources:

- templates
- examples
- boilerplate files

Assets should support the workflow without increasing default context load.

## Harness

Consider a harness layer when the concern is wider than one skill:

- evals
- state or memory
- tool contracts
- approvals
- automation

Do not keep forcing system concerns into `SKILL.md` once they become cross-cutting.

