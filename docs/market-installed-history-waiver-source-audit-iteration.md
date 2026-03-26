# Market Installed History Waiver Source Audit Iteration

This temporary note tracks the next installed-state history waiver source-audit iteration for the local skills market client.

## Goals

- [ ] Audit governance waiver source files against the latest reviewed apply or execute artifacts and detect post-execution drift clearly
- [ ] Expose the source-audit workflow through the unified CLI, documentation, and smoke pipeline
- [ ] Run validation, then delete this note after the iteration is fully complete

## Current Status

- The client can now generate reviewed apply packs and execute them safely in staging mode or mirrored `--write` mode.
- The next gap is post-execution assurance: maintainers still lack a built-in way to confirm governance source files continue to match the latest reviewed apply artifacts after manual edits or later repository changes.
