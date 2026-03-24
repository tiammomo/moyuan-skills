# Build Skills Design Flow

## From Requests to Scope

Start with concrete requests, not abstract capability names.

Collect a short list of prompts a user might actually say, then extract:

- the verb
- the minimal input
- the desired output
- the risk or irreversible edge

If you cannot describe the skill through concrete requests, the trigger is probably still too broad.

## Draft the Trigger Before the Body

Write the `description` early.

A good description does two jobs at once:

- explain what the skill does
- include a clear `Use when ...` clause

If the trigger sentence still sounds like marketing copy, keep narrowing it.

## Write SKILL.md as a Router

`SKILL.md` should answer:

- which path matches this task
- what is unsafe
- what the default workflow is

It should not try to answer every topic in full.

Keep the body short enough that the best next step is obvious.

## Split Content Deliberately

Use this rule of thumb:

- keep routing and guardrails in `SKILL.md`
- move long topic detail into `references/`
- move repeatable execution into `scripts/`
- move copyable output resources into `assets/`

Do not duplicate the same detail across multiple layers unless one layer truly needs the shorter summary.

## Teach Through the Routing Itself

When the skill is educational, the route labels should themselves model good skill writing.

Prefer router entries like:

- "Design a brand-new skill from scratch"
- "Decide what belongs in SKILL.md versus references"

Avoid router entries that only expose filenames without intent.

## Finish With a Check Path

Every skill should leave behind one obvious way to validate that the bundle still makes sense.

At minimum:

- a repository-level structure lint
- a skill-local smoke check

That validation path is part of the skill design, not an afterthought.

