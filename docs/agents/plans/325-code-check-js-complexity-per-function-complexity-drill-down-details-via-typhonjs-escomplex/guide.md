# Guide Plan: code_check js_complexity: per-function complexity drill-down (--details) via typhonjs-escomplex

Main plan: [plan.md](plan.md)

## Shared contracts

Document the user-facing behaviour: `--details [N]`, the `details` config key, the function-line and unavailable-note formats, and the escomplex failure warning, as listed in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Document --details
In `docs/guides/code_check/js_complexity.md`:
- add `--details [N]` to the options table;
- add `details` to the config keys and the example config;
- add an example run with function lines (the spec §4 example);
- explain the `(per-function data unavailable)` note and the `Warning: escomplex failed ...` line;
- state that per-function data never changes levels or the exit code.

Follow `docs/guides/code_check/rubycritic.md`'s `--details` section for tone and layout.

## Files to Change
- `docs/guides/code_check/js_complexity.md`: the `--details` docs.
