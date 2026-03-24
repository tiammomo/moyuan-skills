# Validation Loop

## Minimum Validation Layers

Treat validation as part of the skill design.

For most skills, keep at least two layers:

- a repository-level structure check
- a skill-local smoke check

If the skill includes scripts, add a representative execution path as well.

## What Repository Lint Should Catch

Repository lint should catch structural drift such as:

- invalid frontmatter
- missing required sections
- orphaned reference files
- overgrown `SKILL.md`

These checks protect the shape of the skill.

## What Skill-Local Smoke Checks Should Catch

A skill-local check should answer:

- are the required references present
- are the templates present
- does the local checker still reflect the teaching contract

For execution-heavy skills, add CLI help smoke or a mock self-test.

## Forward-Testing Without Leakage

When the skill is complex, forward-test with a fresh agent or thread on a realistic task.

Pass the task and the skill path.
Do not pass your diagnosis of what you think is broken unless the task truly needs it.

The goal is to see whether the skill generalizes, not whether another agent can reconstruct your intent.

## When to Iterate

Revisit the skill when:

- triggers are too broad
- router branches feel ambiguous
- examples keep rewriting the same logic
- safety rules are buried too deep
- future harness responsibilities are starting to leak into the skill

Good skills are revised through real use, not only through one-time authoring.

