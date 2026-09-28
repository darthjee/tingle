# Guide Plan: check_file_size: add --ignore and --include glob flags

Main plan: [plan.md](plan.md)

## Shared contracts

- The flag behaviour, syntax, anchoring and precedence from [plan.md](plan.md),
  plus the canonical examples listed there.

## Implementation Steps

### Step 1 — Document `--ignore` and `--include` in the user guide
In `docs/guides/check_file_size.md`:
- Add `--ignore GLOB` and `--include GLOB` rows to the Options table
  (default: none; can be repeated).
- Add `### `--ignore` and `--include`` subsections after `### `--exclude`` and
  `### `--ext``. They cover:
  - that globs match the path relative to `<path>`;
  - a short syntax table (`*`, `?`, `[...]`, `**`, `\`);
  - anchoring (no `/` means "any directory", a `/` anchors at `<path>`, a
    trailing `/` means "the whole directory");
  - case-insensitivity;
  - `--ignore` winning over `--include`, and AND with `--ext`;
  - the reminder to quote globs so the shell does not expand them;
  - the canonical examples.
- Mention the single-file behaviour (globs match the file name) in
  "Single-file targets".
- Add one or two of the examples to the "Examples" section.

## Files to Change
- `docs/guides/check_file_size.md` — options table, new subsections and examples.
