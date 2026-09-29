# Plan: check_file_size: add --min-level display filter

Issue: [252-check-file-size-add-min-level-display-filter.md](../../issues/252-check-file-size-add-min-level-display-filter.md)

## Overview
Add a `--min-level ok|warn|error|critical` flag to `tingle check_file_size` that hides table rows below the given level. It only changes which rows are shown. The summary, `Total:` and the `--fail-on` gate keep using every analysed file. The same change stops `--top` from cutting the summary. The spec is [`docs/agents/specs/check_file_size/min-level.md`](../../specs/check_file_size/min-level.md), and section 6 of [`README.md`](../../specs/check_file_size/README.md) covers display vs counting.

## Agents involved

- [python](python.md) — flag, filtering, `Reporter` split, tests.
- [cli](cli.md) — `long_help` in `commands/python.json`.
- [guide](guide.md) — `docs/guides/check_file_size.md`.

## Shared contracts

- **Flag**: `--min-level LEVEL`, `LEVEL` ∈ `ok`, `warn`, `error`, `critical` (case-sensitive, lower case). Default when omitted: `ok` (show everything). Invalid value → usage error on stderr, exit `1`.
- **Order**: OK < WARN < ERROR < CRITICAL (same as `--fail-on`). A row is shown when its level is **at or above** `LEVEL`.
- **Pipeline**: classify → `--min-level` filter → `--top N` (N largest of what is left). Rows stay sorted largest first.
- **Counting**: the `Summary:` line, `Total:` line and `--fail-on` gate always use every analysed file, whatever `--min-level` and `--top` are. **Behaviour change**: before this, `--top` also cut the summary and `Total:`.
- **Empty result**: when no row passes, no table header is printed. Instead stdout shows `No files at or above <LEVEL>.` (level in upper case, e.g. `WARN`), a blank line, then the usual separator, summary and total. Exit `0` unless the gate fails.
- `No files found for analysis.` (nothing collected) is unchanged and takes priority.
- Exit codes are unchanged: `0` ok, `1` usage/path error, `2` gate failed.
