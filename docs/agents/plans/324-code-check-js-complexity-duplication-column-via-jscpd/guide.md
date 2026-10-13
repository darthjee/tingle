# Guide Plan: code_check js_complexity: duplication column via jscpd

Main plan: [plan.md](plan.md)

## Shared contracts

Documents the `Dup` column and the jscpd failure warning exactly as in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Document `Dup` in the user guide
In `docs/guides/code_check/js_complexity.md`:
- update every sample table (around line 657) with the `Dup` column, matching spec section 4's example;
- add a `Dup` row to the column table (around line 705): the number of the file's lines inside exact clones (jscpd, at least 50 tokens and 5 lines), counted once, compared only among the selected files. It is information only, and `-` means not available (parse error, file over 1 MiB, or jscpd failed);
- document the `Warning: jscpd failed in <image>; duplication data is not available: <message>` warning wherever the other warnings are listed.

## Files to Change
- `docs/guides/code_check/js_complexity.md` — the column, the examples and the warning.
