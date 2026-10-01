# Guide Plan: code_check rubycritic: per-method complexity drill-down (--details)

Main plan: [plan.md](plan.md)

## Shared contracts

Document `--details [N]` and the `details` config key as defined in
[plan.md](plan.md#cli-flag-and-config-key), the detail-line layout and the
missing-`methods` error.

## Implementation Steps

### Step 1 — Document `--details`
In `docs/guides/code_check/rubycritic.md`:

- Options table: add `--details [N]`.
- New `### --details` subsection: what it shows, the default of 5, 0 = all, and that only the shown rows get details (interaction with `--top`/`--min-level`). Add an example output block. Say that methods have no levels and don't affect `--fail-on`.
- "Reading the output": describe the indented method lines.
- "Exit status and errors": the error when the image is too old for `--details` (for example with a custom `--image`).
- Examples: add `tingle code_check rubycritic ./app --top 5 --details 3`.
- Config section (if #297 has already added one): add the `details` key.

## Files to Change
- `docs/guides/code_check/rubycritic.md`: as above.
