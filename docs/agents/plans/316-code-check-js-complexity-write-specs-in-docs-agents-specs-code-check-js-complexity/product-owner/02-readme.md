# README.md: shared contracts, sub-issue map, deviations
Write `docs/agents/specs/code_check/js_complexity/README.md`. It holds the contracts used by more than one sub-issue:
- an overview and a link to #315;
- the **sub-issue map** table (sub-issue, what, spec file, depends on) and the **merge order**, both exactly as in the issue's "Sub-issue map";
- the CLI and flags, with defaults `50/60/75` on `fta_score`;
- extensions (core, `.d.ts` skipped, minified, SFC);
- default excludes (`file_size`'s list plus `.turbo`, `.svelte-kit`, `.output`, `.vercel`, `.parcel-cache`, `storybook-static`);
- the filter order;
- the config keys;
- exit codes (0, 1, 2);
- a **summary of the merged JSON contract** (fixed shape, `null` = not available, one entry per stdin line, the per-file state table), linking to `image.md` for the full definition;
- the message style (`Error:`/`Warning:`);
- a **"Deviations from #315"** section, filled from step 01's findings and the decided choices, or "None".

## Files to Change
- `docs/agents/specs/code_check/js_complexity/README.md` — new.
