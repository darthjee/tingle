# Guide Plan: check_file_size: add a flag to fail with non-zero exit status for CI

Main plan: [plan.md](plan.md)

## Shared contracts

Document exactly the flag, gate semantics, exit codes (0/1/2), stream and
colour rules from [plan.md](plan.md#shared-contracts). Base the wording on the
`python` agent's final implementation and `long_help`.

## Implementation Steps

### Step 1 — Document --fail-on and CI usage
In `docs/guides/check_file_size.md`:
- Add `--fail-on LEVEL` to the options table (default: off) and a short
  subsection explaining the "at this level or higher" rule. Say that `--top`
  does not hide files from the gate, and that "No files found" exits 0.
- Add a "Using in CI" example: `tingle check_file_size ./src --fail-on error`.

### Step 2 — Update errors, exit codes and colour sections
- Errors table: path not found now goes to **standard error** (exit 1).
  Unknown option / invalid value now exits **1** (was 2). Add a row for the
  size gate failing (exit 2).
- Replace the sentence saying output is coloured "even when redirected" (around
  line 161) with the new rule: colours only on a TTY, disabled by `NO_COLOR`.
- Check that the guides index (`docs/guides/README.md`) description still fits.

## Files to Change
- `docs/guides/check_file_size.md`: new option, CI example, exit codes, stderr and colour behaviour
- `docs/guides/README.md`: only if the command summary needs a tweak

## Notes
- The current guide documents usage errors as exit `2`. That changes to `1`.
