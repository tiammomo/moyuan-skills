# Tool Contracts

## Why Tool Contracts Matter

A script is not yet a reliable harness component just because it runs.

A usable tool contract should make clear:

- what the command expects
- what it returns
- what can fail
- what safety assumptions hold

Without that contract, the harness has to guess.

## Minimum Contract Fields

For most skill scripts, define at least:

- tool ID
- owning skill
- command surface
- input format
- output format
- failure modes
- safety notes

## Start With Real Tools

The easiest way to build useful contracts is to write them for tools that already exist in the repo.

Good candidates in this repo:

- `release-note-writer`
- `incident-postmortem-writer`

See the example contracts under `examples/harness-prototypes/tool-contracts/`.

