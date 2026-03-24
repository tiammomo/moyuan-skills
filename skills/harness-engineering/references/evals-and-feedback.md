# Evals and Feedback

## Add Evals Before Adding More Magic

When a skill system starts failing in subtle ways, adding more prompt text is usually not enough.

You need feedback loops that show:

- whether outputs are improving
- which routes fail most often
- where tool contracts are unclear

## Useful Eval Layers

Start with lightweight layers:

- replay a representative task
- compare output shape or artifact structure
- run smoke checks around scripts and templates

Then grow toward:

- task sets
- graders
- regression dashboards
- trace review

## Preserve Artifacts

A harness should keep enough trace material to support debugging:

- inputs
- chosen route
- tools used
- key outputs or diffs
- review decisions

That makes failures teachable instead of mysterious.

## Close the Loop

An eval is only useful if it changes the system.

Use failures to decide whether to update:

- the skill trigger
- the router
- the bundled references
- the tool contract
- the system harness

