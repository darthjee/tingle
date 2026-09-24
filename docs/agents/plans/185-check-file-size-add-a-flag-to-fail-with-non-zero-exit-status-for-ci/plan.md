# Plan: check_file_size: add a flag to fail with non-zero exit status for CI

Issue: [185-check-file-size-add-a-flag-to-fail-with-non-zero-exit-status-for-ci.md](../../issues/185-check-file-size-add-a-flag-to-fail-with-non-zero-exit-status-for-ci.md)

## Overview
Make `tingle check_file_size` usable as a CI gate. A new
`--fail-on warn|error|critical` flag exits with status 2 when any collected
file reaches that level. Errors move to stderr, and ANSI colours are turned
off when the stream is not a TTY or `NO_COLOR` is set. The `python` agent
implements the behaviour, its tests and `long_help`. The `guide` agent
updates the user guide.

## Agents involved

- [python](python.md)
- [guide](guide.md)

## Shared contracts

**Flag**: `--fail-on LEVEL`, where `LEVEL` is one of `warn`, `error`, `critical`
(argparse `choices`, lowercase). It is optional; with no default the gate is off.

**Gate semantics**: fails when at least one *collected and analysed* file
(before `--top` is applied) is classified at `LEVEL` or higher
(order: warn < error < critical). The full report is always printed first.
The "No files found for analysis." case exits 0.

**Exit codes** (for `check_file_size` only):

| Code | Meaning |
| --- | --- |
| `0` | Success, or gate passed / not requested |
| `1` | Runtime or usage error: path not found, unknown option, invalid value (e.g. `--top abc`, `--fail-on foo`) |
| `2` | Size gate failed (`--fail-on`) |

Note: usage errors currently exit `2` (argparse default) and the guide
documents that. They move to `1` so that `2` means only "gate failed".

**Streams**: the report goes to stdout. Error messages (`Error: path not found: …`
and argparse usage errors) go to stderr.

**Colour**: ANSI codes are printed on a stream only when that stream
`isatty()` **and** the `NO_COLOR` env var is unset or empty. Otherwise the
output is plain text with the same layout and emoji labels. Stdout and stderr
are decided independently.

**CI example** (used in both `long_help` and the guide):
`tingle check_file_size ./src --fail-on error`
