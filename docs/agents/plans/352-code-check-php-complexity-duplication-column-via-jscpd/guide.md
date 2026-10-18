# Guide Plan: code_check php_complexity: duplication column via jscpd

Main plan: [plan.md](plan.md)

## Shared contracts

Documents the report layout and warning defined in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Document the Dup column
In `docs/guides/code_check/php_complexity.md`: add `Dup` to every example table (header, separator and rows, values from [duplication.md §4](../../specs/code_check/php_complexity/duplication.md#4-report): `13` for `dup_a.php`/`dup_b.php`, `0` for other analysed files, `-` on `PARSE` rows), add a `Dup` row to the column table (lines of the file in exact clones jscpd finds among the selected files, each line once; information only; `0` = checked with no clone, `-` = not available), state that files outside the selection (e.g. `vendor/`) never count, and document the jscpd failure warning and that it leaves the exit code unchanged. Include the `--details` example with the column on file rows.

## Files to Change
- `docs/guides/code_check/php_complexity.md` — `Dup` column, examples, failure warning.
