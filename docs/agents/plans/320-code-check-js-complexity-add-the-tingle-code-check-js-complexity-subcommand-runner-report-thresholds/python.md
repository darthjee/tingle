# Python Plan: code_check js_complexity: add the tingle code_check js_complexity subcommand

Main plan: [plan.md](plan.md)

## Shared contracts

You produce everything listed in [plan.md](plan.md#shared-contracts):
- the subcommand name and its order;
- the one-line description in `CodeCheck.SUBCOMMANDS`;
- the flags with their help texts, types and defaults;
- the extensions, declaration suffixes and default excludes;
- the score and level rules;
- the exit codes and messages, word for word from spec §10.

`cli` (`long_help`), `guide` and `product-owner` copy these values, so any deviation from the spec must be reported back.

Spec: [`subcommand.md`](../../specs/code_check/js_complexity/subcommand.md), [`file-selection.md`](../../specs/code_check/js_complexity/file-selection.md) (§2, §3, §5, §7), [`docker-check.md`](../../specs/code_check/js_complexity/docker-check.md), [`image.md`](../../specs/code_check/js_complexity/image.md#7-merged-json) (merged JSON sample).

## Steps

- [01 — Scaffold the package (constants, errors, flags, wrappers, selection)](python/01-scaffold-package.md)
- [02 — Parse the merged JSON](python/02-output-parser.md)
- [03 — Report table and summary](python/03-reporter.md)
- [04 — Executor, dispatch and completion](python/04-executor-and-registration.md)

## CI Checks
- `python/`: `ruff check .` (CI job runs it in `python/`)
- `python/`: `pytest` (or `make tests` via docker-compose); coverage must stay ≥ 75%.

## Notes
- **`DockerCheck.run` reads `cli["no_config"]`.** `--no-config` only arrives in #322, so `CheckJsComplexity` must override `_load_config` to return `({}, None)` without reading the file. Otherwise the run raises `KeyError`. Leave a short comment that #322 replaces this. Do not add `--no-config` to `FLAGS` here.
- **`.gitignore` must stay off in #320.** `DockerCheck._merge` sets `gitignore=True` by default, and `_selection_options` forwards it. Override `_selection_options` (or the `_select_files` hook) so that #320 passes `gitignore=False`, `ignore=[]` and `include=[]`, and only the default excludes. #321 removes the override.
- `SINGLE_DEFAULTS` has no `details` key, so `_validate` skips the `--details` check by design.
- The parser validates the **whole** merged JSON shape now (`duplication`, `functions`, `jscpd`/`escomplex` versions), even though nothing displays them yet. This way #324/#325 never change the checks.
- Manual end-to-end check: `make js-complexity-image`, then `python/code_check/main.py js_complexity <fixture> --image tingle_js_complexity:dev`. Compare against the spec §6 full example.
- Do not touch `rubycritic/` or `docker_check/`, unless a missing hook makes it unavoidable. In that case keep the change behaviour-neutral for `rubycritic` and mention it in the PR.
