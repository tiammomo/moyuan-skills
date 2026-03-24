# Refactor Playbook

## 1. Inventory the Current Bundle

List what currently exists:

- trigger sentence
- main skill body
- topic-heavy sections
- repeated command sequences
- templates or examples

This gives you the raw material for the split.

## 2. Pull Routing Back Into the Center

Rewrite `SKILL.md` so it only keeps:

- the main safety rules
- the task router
- the default workflow

Everything else now needs to justify staying.

## 3. Move Topic Depth Outward

Take each long subsection and ask:

- is this only needed for one branch
- does it teach topic depth rather than routing

If yes, move it into a reference file.

## 4. Convert Repetition into Execution

When examples keep repeating command sequences or transformation logic, extract a script.

That makes the skill smaller and the behavior more testable.

## 5. Add a Refactor Check

After the split, verify:

- the trigger is still accurate
- every reference is reachable
- the main router is clearer than before

If the skill is now harder to navigate, the split went too far.

