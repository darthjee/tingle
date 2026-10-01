# Product-owner Plan: code_check rubycritic: per-method complexity drill-down (--details)

Main plan: [plan.md](plan.md)

## Shared contracts

The specs must describe the `methods` key and the `details` flag/config key
exactly as in [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Update the rubycritic specs
`docs/agents/specs/code_check/rubycritic/` is still the source of truth for the open #296/#297 until #298 removes it. Keep it consistent:

- `README.md` section 3 (flags table): add `--details` (added by #291, config key `details`). Section 5: add `details` to the config keys. Section 8: stdout is "`report.json` plus `parse_errors` and `methods`".
- `config.md`: add `details` (int ≥ 0 or `null`) to the schema and validation rules.
- `subcommand.md` section 5: add `methods` to the JSON sample and the field table.
- `image.md` section 4: add `methods` to the output contract.

## Files to Change
- `docs/agents/specs/code_check/rubycritic/README.md`, `config.md`, `subcommand.md`, `image.md`.

## Notes
- If #298 has already removed the specs folder, skip this step.
