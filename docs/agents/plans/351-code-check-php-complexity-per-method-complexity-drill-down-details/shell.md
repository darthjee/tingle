# Shell Plan: code_check php_complexity: per-method complexity drill-down (--details)

Main plan: [plan.md](plan.md)

## Shared contracts

The image must produce `files[].functions` as described in [plan.md](plan.md#shared-contracts): `null` for parse errors and refused lines, `[]` for analysed files with no counted unit (including `pdepend: null` files), otherwise `{name, line, ccn, npath}` entries in source order (by `line`, then `name`), with `npath` as an exact JSON integer. `tool_versions` does not change.

## Implementation Steps

### Step 1 — Collect the counted units in the entrypoint
In `docker/php_complexity/lib/pdepend.php`, extend `tpc_summarize` (which already walks the counted units through `tpc_add_unit`) so that it also collects one `{name, line, ccn, npath}` per unit for each staged file. Do not add a second pass or a second PDepend run.
- Name: for a `class`/`trait` owner it is `<owner @name>::<method @name>`; for a `function` it is `@name`. Short names, with no namespace.
- `line` comes from `@start` and is already validated in `tpc_add_unit`. Keep `npath` as a digit string, the same way as `max_npath`, so `tpc_encode_output` writes it as an exact integer. Extend the encoder if it only handles `max_npath`.
- Sort each file's list by `line`, then `name`.
- Return the functions alongside the `pdepend` objects, either as a second array or by changing the return shape, and update the docblocks.

In `docker/php_complexity/entrypoint.php`:
- Set `functions` to `[]` for every staged, non-rejected file, including files PDepend did not list (`pdepend` stays `null`).
- Overwrite it with the collected list where there is one.
- Keep `null` for parse errors (PHP lint or PDepend-rejected) and refused lines.
- Update the header comment (line ~21) that says `functions: null`.

### Step 2 — Smoke test and Docker Hub description
In `scripts/release_image.sh` `smoke_test_php_complexity()`, assert the `functions` column of the fixture table in `docs/agents/specs/code_check/php_complexity/image.md` §9 (grounding values in `details.md` §3):
- the names, lines and `ccn` of every entry for `Calculator.php`, `Shapes.php`, `Modern.php` (no `Suit::color`), `Anon.php` (only `Factory::make`) and `helpers.php`;
- `[]` for `bootstrap.php` and `empty.php`, and `null` for the parse errors and refused lines;
- every `line`/`ccn`/`npath` is an int ≥ 1;
- `sum(ccn) == pdepend.ccn` for every analysed file.

Update `docker/php_complexity/DOCKERHUB_DESCRIPTION.md` so it describes the per-function data and no longer says that `functions` is always `null`.

## Files to Change
- `docker/php_complexity/lib/pdepend.php` — collect the per-unit entries in `tpc_summarize`/`tpc_add_unit`.
- `docker/php_complexity/lib/output.php` — only if `tpc_encode_output` needs to encode `functions[].npath` as an exact integer.
- `docker/php_complexity/entrypoint.php` — fill `functions` (`[]`/list/`null`); header comment.
- `scripts/release_image.sh` — `smoke_test_php_complexity` assertions on `functions`.
- `docker/php_complexity/DOCKERHUB_DESCRIPTION.md` — mention the per-function data.

## CI Checks
- `docker/php_complexity`: `scripts/release_image.sh build php_complexity && scripts/release_image.sh smoke-test php_complexity` (CI job: the php_complexity release/smoke-test workflow in `.circleci/config.yml`).

## Notes
- Abstract methods are listed with `ccn` 1. Bare `method` elements (enum methods, some anonymous-class methods) and owners without a `file` child are never counted, the same as today.
- The data of a PDepend-rejected file must be discarded (it gets `functions: null`), just as its `pdepend` data is today.
