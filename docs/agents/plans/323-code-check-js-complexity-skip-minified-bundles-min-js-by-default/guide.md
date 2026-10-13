# Guide Plan: code_check js_complexity: skip minified bundles (*.min.js) by default

Main plan: [plan.md](plan.md)

## Shared contracts

- Minified bundles: names ending in `.min.js`, `.min.mjs`, `.min.cjs`, any case. Skipped by default, silently.
- Only `--no-default-excludes` or `"no_default_excludes": true` turns the skip off (no separate switch).
- `--include` never brings them back (`--include '**/*.min.js'` alone selects nothing).
- A minified single-file `<path>` is skipped (exit 0) unless `--no-default-excludes`; directory excludes still never apply to a single file.
- `.min.ts` is not a minified bundle; a minified file without `.min` in its name is analysed — suggest `--ignore`.
- `--no-default-excludes` help: `Do not skip the default directories or minified bundles; only --exclude names apply`.

## Implementation Steps

### Step 1 — Update docs/guides/code_check/js_complexity.md
- Flags table (`--no-default-excludes` row, ~line 78): new help text.
- Extensions section (~line 178): after the declaration-files paragraph, add a minified-bundles paragraph with the rules above, and note `--no-default-excludes` brings them back but `--include` does not.
- `--no-default-excludes` section (~line 228): say it also drops the minified skip; declaration files still stay skipped.
- Filter order (~line 343): step 6 becomes "declaration files, always; then minified bundles, unless `--no-default-excludes`".
- Single-file targets (~line 355): the minified rule applies to a single file, unlike the directory excludes.
- Config table `no_default_excludes` row (~line 466): mention minified bundles if the row describes what it drops.
- Limitations (~line 861): replace "Minified bundles are analysed ... planned (#323)" with: `*.min.js`-style bundles are skipped by default; a minified file without `.min` in its name is still analysed and gets a high score — use `--ignore` for those.

## Files to Change
- `docs/guides/code_check/js_complexity.md` — the sections above.

## Notes
- No change to `docs/guides/README.md` or other guides.
