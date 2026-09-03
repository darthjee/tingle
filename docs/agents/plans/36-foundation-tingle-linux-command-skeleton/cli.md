# Cli Plan: Foundation: tingle linux command skeleton

Main plan: [plan.md](plan.md)

## Shared contracts

Depends on `shell`'s entry point path `shell/linux/main.sh` (see
[shell.md](shell.md)) and its two surfaced subcommands, `shell` and `sed`
(both stubbed in this issue; real behavior in #37/#38).

## Implementation Steps

### Step 1 — Register the `linux` command

Add a `linux` entry to `commands/shell.json`, following the `install`
entry's format:

```json
"linux": {
  "path": "shell/linux/main.sh",
  "short_help": "Run GNU/Linux tools (sed, shell) inside a container.",
  "long_help": "Runs real GNU/Linux command-line tools inside a Docker container (the current working directory mounted in at the same path), for cases where the host tool differs from its Linux counterpart in ways that break scripts or muscle memory — e.g. macOS's BSD sed vs GNU sed.\n\nUsage:\n    tingle linux shell\n    tingle linux sed <sed-args...>"
}
```

Match the descriptive style already used for the `kube` entry in
`commands/python.json` (usage examples in `long_help`). Both `shell` and
`sed` are stubs at this point (#37/#38 implement them for real) — the help
text still documents the intended usage since it is user-facing from the
moment `tingle linux --help` is run.

## Files to Change
- `commands/shell.json` — add the `linux` entry (`path`, `short_help`,
  `long_help`).

## Notes
- No `completion.sh` exists for `linux` in this issue, so no change is
  needed in `completions/bash/commands.sh` — the generic file/folder
  completion fallback already applies.
