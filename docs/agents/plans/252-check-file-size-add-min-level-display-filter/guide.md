# Guide Plan: check_file_size: add --min-level display filter

Main plan: [plan.md](plan.md)

## Shared contracts

- `--min-level ok|warn|error|critical`, default `ok`, rows at or above the level, applied before `--top`.
- The summary, `Total:` and `--fail-on` always count every analysed file. `--top` no longer cuts the summary.
- With no matching rows, the output is `No files at or above <LEVEL>.` followed by the summary.

## Implementation Steps

### Step 1 — Options table and `--min-level` section
In `docs/guides/check_file_size.md`, add a row to the Options table: `--min-level LEVEL` | `ok` | "Show only files at `LEVEL` or higher…". Add a `### --min-level` section, after `--top` or before `--fail-on`, that covers: the level order, display-only behaviour, the order of `--min-level` then `--top`, the empty-result note (with a sample output), and the examples from the spec (`--min-level warn`, `--min-level error --top 5`, `--min-level critical --fail-on error`).

### Step 2 — Fix the `--top` summary wording
In "Reading the output" → Table/Summary, replace "With `--top`, both lines only count the rows shown…" with text saying that the summary and total always count every analysed file, even when `--top` or `--min-level` hide rows. Update the `--top` note in the Table section and the `--fail-on` bullet so they also mention `--min-level`.

## Files to Change
- `docs/guides/check_file_size.md` — options table, new section, summary wording.
