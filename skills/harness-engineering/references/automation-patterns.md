# Automation Patterns

## Automation Is Not Just Scheduling

Useful automation specs should define:

- what runs
- when it runs
- what inputs it reads
- what checks run before and after
- whether human review is required

## Good First Automation Targets

Start with repeatable, reviewable reporting workflows:

- weekly triage summaries
- release note generation
- recurring audit reports

These workflows are easier to automate than high-risk mutating workflows.

## Include Guardrails in the Spec

A good automation plan should state:

- the prechecks
- the output destination
- who reviews the result
- what blocks execution

See the example under `examples/harness-prototypes/automation/`.

