# Product-owner Plan: check_file_size: load options from ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

Bring the specs in line with [plan.md](plan.md#shared-contracts), which adds `--no-config` and the `Config:` header line to the original spec.

## Implementation Steps

### Step 1 — Update the specs
- `docs/agents/specs/check_file_size/config.md`: add `--no-config` (skips load and validation), the `Config: <path>` header line (shown only when a section was loaded), `load_section` returning `None` for a missing file/section (so "missing" and "empty" differ), and threshold ordering explicitly out of scope; add matching tests to "Tests expected".
- `docs/agents/specs/check_file_size/README.md`: add `--no-config` to the section 3 flags table (config key: none) and mention it in section 4.

## Files to Change
- `docs/agents/specs/check_file_size/config.md` — `--no-config`, header line, `load_section` return value.
- `docs/agents/specs/check_file_size/README.md` — flags table and precedence note.
