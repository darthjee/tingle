# Product-owner Plan: code_check php_complexity: per-method complexity drill-down (--details)

Main plan: [plan.md](plan.md)

## Shared contracts

Document the `files[].functions` contract exactly as in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Update the image doc
In `docs/agents/tingle-php-complexity-image.md`:
- Replace "It has no per-function data … `functions` … always `null`" (line ~15) and the `files[].functions` table row (line ~224, "Always `null` in this version") with the real contract: which units are counted, the `null`/`[]`/list cases, source order, and `sum(ccn) == pdepend.ccn`.
- Update the JSON example (lines ~184–188) so `functions` holds real entries, and `[]` for `bootstrap.php`.
- Add the `functions` column to the fixture table.

Take everything from `docs/agents/specs/code_check/php_complexity/details.md` §3 and `image.md`.

## Files to Change
- `docs/agents/tingle-php-complexity-image.md` — describe the per-function data.

## Notes
- If the shell agent's smoke test shows grounding values different from the spec, correct the specs (`details.md`, `image.md`) to match the real image, as was done for #325.
