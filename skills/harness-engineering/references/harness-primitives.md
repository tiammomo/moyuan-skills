# Harness Primitives

## Skills Are Not the Whole System

A skill is a reusable knowledge and workflow bundle.

A harness is the system layer that decides:

- when to use the skill
- how tools are called
- what state is preserved
- where review or approval happens

If a concern spans multiple skills, it is usually a harness concern.

## Core Primitives

The smallest useful harness model usually includes:

- trigger selection
- tool contracts
- state or memory boundaries
- eval and trace capture
- safety gates
- automation or scheduling

You do not need to implement all of them at once, but you should know which ones are missing.

## Skill vs Harness Boundary

Keep these in the skill when they are local to one workflow:

- domain knowledge
- task router
- workflow hints

Move these toward the harness when they become cross-cutting:

- approval logic
- execution policy
- memory persistence
- eval pipelines
- run orchestration

## Design for Explicit Contracts

Tools should not just exist; they should have contracts:

- expected inputs
- expected outputs
- failure modes
- safety assumptions

Loose contracts are one of the fastest ways for a growing skill system to become unreliable.

