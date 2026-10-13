# Python Plan: code_check js_complexity: skip minified bundles (*.min.js) by default

Main plan: [plan.md](plan.md)

## Shared contracts

- `Constants.MINIFIED_SUFFIXES = (".min.js", ".min.mjs", ".min.cjs")`, matched on `path.name.lower()`.
- The skip is on unless `no_default_excludes` resolves to true (flag or config). Declaration files are always skipped.
- `--include` never brings minified files back; a minified single-file `<path>` is skipped (exit 0) unless `--no-default-excludes`.
- `--no-default-excludes` help: `Do not skip the default directories or minified bundles; only --exclude names apply`.

## Steps

- [01 — Add the minified constant and predicate](python/01-minified-predicate.md)
- [02 — Wire no_default_excludes into the selection](python/02-wire-executor.md)
- [03 — Update the --no-default-excludes help](python/03-flag-help.md)
- [04 — Tests](python/04-tests.md)

## CI Checks
- `python`: `cd python && ruff check . && pytest` (CI jobs: the ruff and pytest jobs in `.circleci/config.yml`)

## Notes
- Keep `docker_check` unchanged: the binding happens in `js_complexity` only, so `rubycritic` and `file_size` selection tests pass unchanged.
- The skip is silent and counted nowhere, like a default exclude.
