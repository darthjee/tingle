# Guide Plan: code_check php_complexity: per-method complexity drill-down (--details)

Main plan: [plan.md](plan.md)

## Shared contracts

User-visible behaviour: `--details [N]` (alone means 5, `0` = all, a negative value is an error). The dim unit lines use the format `ccn <ccn>  npath <npath>  <Class::method|function>  (<path>:<line>)` and appear only under shown level rows. A row from an older image shows `(per-function data unavailable)`. The config key is `details` (integer ≥ 0 or `null`).

## Implementation Steps

### Step 1 — Document `--details` in the php_complexity guide
In `docs/guides/code_check/php_complexity.md`, follow the structure of `docs/guides/code_check/js_complexity.md`:
- an intro mention linking to `#--details`;
- a `--details [N]` row in the options table;
- `--details N` in the "whole numbers, 0 or more" validation note;
- `details` in the config keys;
- a `### --details` section with the example from `details.md` §4 (`--warn 4 --error 6 --critical 10 --min-level warn --details 2`). It should also cover which units are listed: methods as `Class::method`, functions by name, and no closures, arrow functions, enum methods or anonymous-class methods.

## Files to Change
- `docs/guides/code_check/php_complexity.md` — document `--details` and the `details` config key.

## Notes
- Use the real grounding values from the spec. Do not invent output.
