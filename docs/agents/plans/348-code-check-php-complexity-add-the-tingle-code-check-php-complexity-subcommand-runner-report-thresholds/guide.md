# Guide Plan: code_check php_complexity: add the tingle code_check php_complexity subcommand (runner, report, thresholds)

Main plan: [plan.md](plan.md)

## Shared contracts

Documents the user-visible behaviour in [plan.md § Shared contracts](plan.md#shared-contracts). The content list comes from [`cli.md`](../../specs/code_check/php_complexity/cli.md) §1 ("Docs in the same PR").

## Implementation Steps

### Step 1 — Write the php_complexity guide
Create `docs/guides/code_check/php_complexity.md`, modelled on `js_complexity.md`. Cover:
- usage, and the requirement for Docker;
- the total-CCN metric and the calibration behind 20/40/60 (spec README §3);
- the columns;
- the enum and anonymous-class undercount and the property-hook limitation (README deviations 7 and 8);
- `PARSE` rows for PHP and PDepend rejections, with the hint to try a newer image via `--image` (deviation 2);
- `--ignore`/`--exclude` advice for tests and generated code, marked as coming with #349;
- the Podman note;
- exit codes;
- the §6 full example.

### Step 2 — Update the indexes
Add the `php_complexity` row and name to `docs/guides/code_check.md`, and the nested entry to `docs/guides/README.md`.

## Files to Change
- `docs/guides/code_check/php_complexity.md` — new guide
- `docs/guides/code_check.md` — add the subcommand
- `docs/guides/README.md` — nested entry
