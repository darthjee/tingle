# Issue: Add Auto Complete

## Description

Add bash auto-complete for `tingle` command names, plus a `tingle install` command that wires the completion (and `tingle` itself) into the user's shell via `~/.bashrc`.

## Problem

`tingle` has no bash auto-complete, so users must remember or look up exact command names before typing them. Each JSON file in `commands/` maps command names to metadata (`path`, `short_help`, `long_help`); those top-level keys are the canonical command names, but nothing currently surfaces them to the shell.

There is also no installer: getting `tingle` onto `PATH` and wiring up completion both currently require manual, undocumented steps.

Note: `tingle help` / `tingle --help` (list of available commands and general usage, same as `tingle` with no arguments) is **already implemented** in `bin/tingle` — no new work needed there, just keep it backward-compatible.

## Expected Behavior

- Typing `tingle ` and pressing TAB completes with the list of available command names, derived from the top-level keys of `commands/*.json`.
- Running `tingle install`:
  - Adds `tingle` to the user's `PATH` via `~/.bashrc`.
  - Adds a source line for the bash completion script (`completions/tingle.bash`) via `~/.bashrc`.
  - Is idempotent — running it multiple times does not duplicate entries.
- `tingle`, `tingle help`, and `tingle --help` continue to behave exactly as they do today.

### In Scope

- Bash auto-complete: `tingle` + TAB completes with command names extracted from `commands/*.json` (top-level keys of each JSON file). Completion script lives at `completions/tingle.bash`.
- `tingle install` command: adds `tingle` to PATH and installs bash completion via `~/.bashrc`. Idempotent — detects existing entries and skips if already installed.
- Shell target: Bash only.

### Out of Scope

- Zsh, Fish, or other shell support (future issue).
- `tingle uninstall` command (separate issue).
- `tingle help <command>` — per-command help showing `long_help` (future issue).
- Auto-complete of command arguments, flags, or subcommands — scope is completing command names only.

## Solution

### Command Discovery

Read `commands/*.json` keys directly (chosen): parse each JSON file in `commands/` and extract top-level keys as command names.

- Alternative — parse script filenames in `bin/`: rejected, fragile (filename ≠ command name, no metadata available).
- Alternative — execute each script with `--list`: rejected, adds coupling and runtime cost to completion.

Commands with the same name across JSON files: `bin/tingle` already loads files in alphabetical order and the first file to define a given command name wins. The completion script must match this behavior (or defer to `bin/tingle`'s own resolution) to avoid completing a name that `tingle` itself would not treat as pointing to that command.

### Completion Script Location

The bash completion script lives at `completions/tingle.bash`. `tingle install` sources this file (by absolute path, resolved from the repo root, mirroring how `bin/tingle` resolves `TINGLE_FOLDER`) from `~/.bashrc`.

`completions/` is a new top-level folder; it is owned by the `shell` specialist agent (extending its existing scope over `shell/`), since both the completion script and the `tingle install` logic are bash/shell concerns.

### Install Command Implementation

`tingle install` is implemented as a new dispatched command — an entry in `commands/shell.json` pointing to a new `shell/install.sh`, consistent with how every other command works. `bin/tingle` stays a thin dispatcher and does not special-case `install` the way it special-cases `help`/`--help`.

### Install Mechanism

Append a source line to `~/.bashrc` (chosen): simple, portable, user-level, no sudo required. Requires the user to reload the shell or source `~/.bashrc` afterward.

- Alternative — copy to `~/.local/share/bash-completion/completions/`: rejected, not all systems support this path, less obvious to debug.
- Alternative — copy to `/etc/bash_completion.d/`: rejected, requires sudo, not appropriate for a personal utility repo.

### Edge Cases

- Empty JSON files: `commands/node.json` and `commands/shell.json` are currently `{}`. Auto-complete must handle empty JSON gracefully (no completions from that file, no error).
- Malformed JSON: if a file in `commands/` is not valid JSON, the completion should skip it and not crash.
- `tingle install` run multiple times: must detect existing PATH entry and source line in `~/.bashrc` and skip — no duplicate lines.
- `tingle install` when `~/.bashrc` does not exist: should create the file or handle the absence gracefully.
- `~/.bashrc` already has a source line for a different completion script: must not clobber unrelated entries — only manage tingle-specific lines.

### Backward Compatibility

This is a new feature — no existing behavior is broken.

- `tingle` without arguments, and `tingle help`/`tingle --help`, continue to work as they do today — unchanged by this issue.
- `tingle install` modifies `~/.bashrc` but only adds new lines — existing content is preserved.

### Testing Strategy

- Unit: JSON parsing of `commands/*.json` — valid JSON, empty JSON (`{}`), malformed JSON, missing files.
- Unit: idempotency of install — run twice, assert `~/.bashrc` has exactly one PATH entry and one source line.
- Integration: source the completion script in a bash subshell and verify `COMPREPLY` is populated correctly after `tingle `.
- Integration: run `tingle install` in a temp environment with a mock `~/.bashrc`, verify entries are added, then run again and verify no duplicates.
- Manual: run `tingle install`, open a new terminal, type `tingle` + TAB, verify command names appear.

### Performance and Security

**Performance**: completion must be fast (instantaneous on TAB). Reading and parsing `commands/*.json` on every TAB press is acceptable given the small number of files and their size. No caching required at this stage.

**Security**:
- `tingle install` writes to `~/.bashrc` — must only append, never overwrite. Use a marker comment (e.g., `# >>> tingle >>>` / `# <<< tingle <<<`) to identify tingle-managed lines and make removal safe in the future.
- Completion script must not execute arbitrary code from JSON files — only read and parse keys, never eval or source the JSON content.

## Benefits

- Faster, error-free command entry — no need to memorize or look up exact command names.
- One-step onboarding: `tingle install` gets both `PATH` and completion working without manual `~/.bashrc` edits.
- Command names stay in sync with `commands/*.json` automatically, with no extra maintenance.
