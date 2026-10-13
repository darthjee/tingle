# Plan: code_check js_complexity: skip minified bundles (*.min.js) by default

Issue: [323-code-check-js-complexity-skip-minified-bundles-min-js-by-default.md](../../issues/323-code-check-js-complexity-skip-minified-bundles-min-js-by-default.md)

## Overview
`tingle code_check js_complexity` skips files named `*.min.js`, `*.min.mjs` and `*.min.cjs` (any case) by default, through the `skip` predicate of `docker_check.selection.select_files`. The skip is turned off only by `no_default_excludes` (flag or config), applies to a single-file `<path>` too, and `--include` never brings minified files back. The behaviour is specified in `docs/agents/specs/code_check/js_complexity/file-selection.md` (sections 1, 2, 4, 5 and 9). `docker_check`, `file_size` and `rubycritic` do not change.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

- Minified suffixes, matched on `path.name.lower()`: `.min.js`, `.min.mjs`, `.min.cjs`. `.min.ts` and others are not minified.
- The skip is on unless `no_default_excludes` resolves to true (`--no-default-excludes` or `"no_default_excludes": true`). No separate flag or config key.
- `--include` only narrows: `--include '**/*.min.js'` alone selects nothing.
- Single-file `<path>` that is minified: skipped (`NO_FILES_MESSAGE`, exit 0) unless `--no-default-excludes`. Directory excludes still never apply to a single file.
- Declaration files stay skipped always.
- Filter order step 6 becomes: declaration files (always), then minified bundles (unless `no_default_excludes`).
- New `--no-default-excludes` help text (exact): `Do not skip the default directories or minified bundles; only --exclude names apply`.
