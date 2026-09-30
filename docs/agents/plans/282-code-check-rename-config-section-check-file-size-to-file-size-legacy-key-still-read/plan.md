# Plan: code_check: rename config section check_file_size to file_size (legacy key still read)

Issue: [282-code-check-rename-config-section-check-file-size-to-file-size-legacy-key-still-read.md](../../issues/282-code-check-rename-config-section-check-file-size-to-file-size-legacy-key-still-read.md)

## Overview
The `file_size` subcommand reads its options from a `file_size` section of
`~/.tingle/code_check/config.json` instead of `check_file_size`. The legacy
`check_file_size` section is still accepted, with a deprecation warning on
stderr. Setting both sections is a config error. The python agent adds a
generic `load_sections` helper, so the file is read once, and implements the
rules in the executor. The cli agent updates the `code_check` help text. The
guide agent updates the two user guides. Removing the legacy key is tracked
in #286.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

- Config section name: `file_size`. Legacy section name: `check_file_size`.
  In code: `CONFIG_SECTION = "file_size"`, `LEGACY_CONFIG_SECTION = "check_file_size"`
  in `python/code_check/file_size/executor.py`.
- Behaviour matrix (file present, `--no-config` not given):

  | `file_size` | `check_file_size` | Result |
  |---|---|---|
  | present | absent | Loaded and validated. No warning. |
  | absent | present | Warning on stderr, then loaded and validated like `file_size`. If it is invalid, the warning is followed by the usual `Error: ...` and exit 1. |
  | present | present | `Error: ...` (below), exit 1, no stdout, no warning. |
  | absent | absent | Built-in defaults, no output. |

- Exact warning line (stderr, yellow via `Palette(sys.stderr)`, plain when
  stderr is not a TTY or `NO_COLOR` is set):
  `Warning: <config path>: 'check_file_size' section is deprecated; rename it to 'file_size'.`
- Exact error line (stderr, same path as every other `ConfigError`):
  `Error: <config path>: both 'file_size' and 'check_file_size' sections are set; keep only 'file_size'`
- Structural errors still come first. If either section is not a JSON object,
  the existing `'<name>' must be an object` error is raised, naming the
  offending section.
- The `Config: <config path>` header line appears whenever either section was loaded.
- `--no-config`: the file is not read. No warning, no error.
- Other top-level keys are still ignored.
