# Resource Planning Rules

## Put the Smallest Stable Surface in SKILL.md

`SKILL.md` should keep only what is needed immediately after the skill triggers:

- the task router
- the default workflow
- the main safety constraints

If a paragraph is useful only for one branch of work, it probably belongs in `references/`.

## Use references/ for Topic Depth

Move content into `references/` when it is:

- longer than the router should carry
- specific to one sub-problem
- useful context, but not always needed

Reference files should be grouped by topic, not by the history of how the skill was written.

## Use scripts/ for Repeatable Execution

Move work into `scripts/` when it is:

- easy to get wrong by hand
- repeated often
- easier to validate as code than as prose

If the same command sequence keeps reappearing in examples, that is usually a script candidate.

## Use assets/ for Copyable Output Resources

Use `assets/` when the file is meant to be reused as output material:

- templates
- boilerplate files
- example artifacts

Assets should support the workflow without forcing the agent to preload more text into context.

## Keep Some Things Out of the Skill Entirely

Do not stuff these into the skill bundle:

- repository history
- meeting notes
- changelogs
- long setup narratives

If humans need that material, place it in repository docs instead.

## A Simple Placement Test

Ask four questions in order:

1. Must the agent see this as soon as the skill triggers?
2. Is this only relevant for one sub-task?
3. Is this better executed than explained?
4. Is this meant to be copied into final output?

The first "yes" usually tells you where the content belongs.

