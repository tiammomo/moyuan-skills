# Safety Gates

## What a Safety Gate Should Do

A safety gate exists to prevent a dangerous action from becoming a silent default.

Typical gate triggers:

- public publication
- destructive write
- high-severity incident communication
- customer-visible summary generation

## Minimum Safety Gate Fields

Most gates should declare:

- trigger condition
- required checks
- approval requirement
- blocking conditions
- audit artifacts

## Start With Publication Flows

Publication is a strong first safety gate example because the boundary is clear:

- a draft can be generated automatically
- publication still requires review

See the example under `examples/harness-prototypes/safety-gates/`.

