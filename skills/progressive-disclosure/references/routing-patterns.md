# Routing Patterns

## Route by Intent, Not by Filename

Good router entries name the user's problem first and the file second.

Prefer:

- "Refactor a monolithic skill into layers"

Over:

- "Read refactor-playbook.md"

The filename is support material, not the primary route label.

## Keep Reference Hops Shallow

Every reference should be reachable directly from `SKILL.md`, or at most via one routing reference.

Deep link chains make the skill harder to navigate and harder to validate.

## Add Contents to Long References

If a reference file grows beyond 100 lines, add a `## Contents` section at the top.

That makes previewing and targeted loading much easier.

## Keep Safety Near the Top

If a safety constraint matters before reading a deeper guide, keep it in `SKILL.md`.

References can expand on the rule, but should not be the first place the rule appears.

## Use One Primary Entry Per Task

Router entries can mention a second resource when necessary, but every task should still have one obvious first stop.

That reduces ambiguity when the skill is triggered under pressure.

