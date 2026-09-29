# Guide Plan: check_file_size: load options from ~/.tingle/code_check/config.json

Main plan: [plan.md](plan.md)

## Shared contracts

Document the behaviour in [plan.md](plan.md#shared-contracts) as the source of truth for the user-facing wording.

## Implementation Steps

### Step 1 — Configuration file section
Add a "Configuration file" section to `docs/guides/check_file_size.md` (after "Options", before "Skipped files"): location, JSON example, keys table (key, type, flag), precedence rules with a worked example (config `ignore` + CLI `--ignore` both apply; CLI `--warn` wins), what happens with missing file/section, the error message format and exit 1, and `--no-config` as the way to run without it (e.g. when the config sets `fail_on` or `gitignore: false`).

### Step 2 — Options, header and exit status
Add `--no-config` to the Options section; mention the dim `Config:` line under "Reading the output" → "Header"; add "invalid config file" to "Exit status and errors"; add a config example to "Examples"/"Using in CI" if it fits.

## Files to Change
- `docs/guides/check_file_size.md` — new "Configuration file" section, `--no-config`, header line, exit status.
