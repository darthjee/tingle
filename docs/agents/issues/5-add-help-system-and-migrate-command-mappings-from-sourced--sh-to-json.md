# Issue: Add help system and migrate command mappings from sourced .sh to JSON

## Description

Add a proper `--help`/`help` system to the `bin/tingle` dispatcher, and migrate
command registration from sourced `commands/*.sh` files to declarative
`commands/*.json` files so each command can carry short and long help text
alongside its script path.

## Problem

`bin/tingle` currently sources `commands/*.sh` files, where each defines shell
variables mapping a command name to a script path (`command_name=path/to/script`),
resolved at dispatch time via bash indirect expansion (`${!1}`).

This has two problems:

1. **No real help output.** Calling `tingle` with no arguments only prints a
   terse `Usage: tingle <command> [args...]` line; an unknown command only
   prints a flat, undescribed `Available commands: cmd1,cmd2,...` list. There
   is no way to see what a command does without opening its script.
2. **Commands are sourced as trusted shell code**, not declared as data. There
   is no structured place to attach metadata (like a description) to a
   command without adding more ad-hoc shell variables.

## Expected Behavior

- `tingle`, `tingle help`, and `tingle --help` are all equivalent: each prints
  the general help (every registered command with its `short_help`) and
  exits `0`.

  ```
  Usage: tingle <command> [args...]

  Commands:
    rename        Bulk rename files using pattern matching
    check_size    Check file sizes against a threshold
    ...
  ```

- `tingle --help <command>` prints that command's `long_help` and exits `0`.
- An unknown command still prints `Error: command '<x>' not found.` and exits
  non-zero, but the command list that follows is now the same formatted
  (`name  short_help`) listing used by `--help`, replacing today's flat
  `Available commands: a,b,c` line.

### Non-Goals (out of scope)
- Subcommand nesting (e.g., `tingle python rename`)
- Auto-generating help from script headers
- Removing the `commands/` directory structure
- A dependency-free (non-`jq`) JSON parsing path
- A fallback/coexistence period supporting both `.sh` and `.json` mappings

## Solution

### 1. Migrate command definitions from sourced `.sh` to declarative `.json`

Replace `commands/*.sh` with `commands/*.json`, one file per language
(`commands/python.json`, `commands/node.json`, `commands/shell.json`) —
mirroring today's per-language `.sh` layout. This is a hard cutover: the
`.sh` files are removed in the same change, with no coexistence/fallback
period (only one command, `check_file_size`, is registered today, so there's
no real migration burden).

Each JSON file maps command names to metadata:

```json
{
  "rename": {
    "path": "python/rename_files.py",
    "short_help": "Bulk rename files using pattern matching",
    "long_help": "Renames files in a directory matching a regex pattern. Supports dry-run mode and recursive operation."
  }
}
```

### 2. `bin/tingle` reads JSON via `jq`

`jq` is accepted as a new hard dependency for `bin/tingle` (available on the
maintainer's machine) — no dependency-free parsing path is needed.

Command names are resolved in glob load order (alphabetical:
`node.json`, `python.json`, `shell.json`). On a name collision across files,
the first file that defines a given name wins silently — this is not an
error condition.

### 3. Help output

`bin/tingle` builds the general help listing and per-command long help
directly from the parsed JSON metadata (see Expected Behavior above).

### 4. Edge cases

- **Missing `short_help`/`long_help`**: if a command entry omits either
  field, show placeholder text (e.g. `(no description)`) in its place
  rather than erroring or leaving it blank.
- **Malformed JSON**: an invalid `commands/*.json` file is a hard error —
  `bin/tingle` prints a clear message naming the bad file and exits
  non-zero, rather than dispatching with partial command data.
- **`path` pointing to a missing script**: not validated eagerly. This only
  surfaces at dispatch time, when `exec`ing that specific command actually
  fails — the same as today's implicit behavior. `--help`/listing does not
  check that registered paths exist on disk.
- **`tingle --help <command> <extra args>`**: extra trailing arguments are
  ignored; the command's `long_help` is printed and the call exits `0`.

### 5. Documentation updates

`README.md` and `.claude/agents/cli.md` both currently describe `commands/`
as `commands/*.sh` files "sourced as trusted shell code" — both need
updating to reflect the JSON-based, declarative-data format.

## Benefits

- Commands become self-documenting — `short_help`/`long_help` live next to
  the path mapping instead of requiring someone to open each script.
- Command registration moves from sourced (trusted shell code) to
  declarative data, making it safer and easier to validate or tool around.
- Consistent, predictable help output whether the user asks for it
  explicitly (`--help`/`help`), gets it by default (no args), or hits an
  unknown command.
