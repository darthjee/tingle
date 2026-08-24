# Issue: Add tingle hub

## Description
Add a unified CLI entry point, `bin/tingle`, that routes commands to the correct script under `python/`, `node/`, or `shell/` based on a per-language mapping in `commands/`, replacing the current scattered `bin/` scripts.

## Problem
Currently, tingle scripts are scattered across `bin/`, `python/`, `node/`, and `shell/` with no unified entry point. Users need to know the exact path and language of each script to run it.

## Expected Behavior
```bash
# Execute a python script
tingle check_file_size path/
# → executes: {TINGLE_FOLDER}/python/check_file_size.py path/

# Command with multiple args
tingle check_file_size path/ --max-size 500KB
# → executes: {TINGLE_FOLDER}/python/check_file_size.py path/ --max-size 500KB

# Unknown command
tingle nonexistent
# → Error: command 'nonexistent' not found.
#   Available commands: check_file_size, ...
# → exit 1

# No arguments
tingle
# → Usage: tingle <command> [args...]
# → exit 1
```

## Solution

### Requirements

#### 1. Move `bin/check_file_size.py` → `python/`
Relocate the existing script from `bin/` to `python/` so that `bin/` contains only entry points (not the scripts themselves).

#### 2. Create `bin/tingle` — CLI hub
A shell script that receives `tingle <command> [args...]`, looks up the command name in the `commands/` mappings, and executes the corresponding script with the provided args.

#### 3. Create `commands/` directory at repo root
Each file in `commands/` represents one language/runtime and maps command names to script paths. Format: shell-sourceable files with `key=value` pairs.

**Example — `commands/python.sh`:**
```bash
# commands/python.sh
# Maps command names to script paths (relative to TINGLE_FOLDER)
check_file_size="python/check_file_size.py"
```

**Example — `commands/node.sh`:**
```bash
# commands/node.sh
# Maps command names to script paths (relative to TINGLE_FOLDER)
# (add node commands here)
```

Create `commands/node.sh` and `commands/shell.sh` as empty scaffolds (header comment only, no mappings) alongside `commands/python.sh`, so the per-language file convention is visible even before any node/shell commands exist.

#### 4. TINGLE_FOLDER discovery
`bin/tingle` resolves `TINGLE_FOLDER` as the repository root, using the script's own location:
```bash
TINGLE_FOLDER="$(cd "$(dirname "$0")/.." && pwd)"
```
This avoids dependency on environment variables and works from any working directory.

#### 5. Load mechanism
`bin/tingle` sources all files in `commands/`:
```bash
for cmd_file in "$TINGLE_FOLDER/commands/"*.sh; do
    source "$cmd_file"
done
```
Then looks up the first argument (`$1`) across all sourced mappings using bash indirect parameter expansion — `path="${!1}"` — and executes the corresponding script with the remaining args via `shift; "$path" "$@"`. No `eval` is used: `${!1}` is bash's built-in mechanism for "the value of the variable whose name is stored in `$1`," avoiding the risks of constructing/evaluating a shell string from user input. If `${!1}` expands to empty, that's the "command not found" case.

#### 6. Error handling
- If the command is not found in any mapping: print error message + list of available commands, exit with code 1
- If no arguments provided: print usage info, exit with code 1

### Alternative Solutions
Considered and rejected in favor of the per-language `commands/*.sh` sourced-mapping design above:
- **Single manifest file** (one `commands.sh` with all `command=path` pairs across languages) — rejected; loses the per-language file organization this issue is built around.
- **Convention-based discovery** (no mapping files; infer script path from command name + fixed search order) — rejected; couples command names to filenames and removes the ability to name a command differently from its script.
- **Hardcoded `case` statement in `bin/tingle`** — rejected; requires editing `bin/tingle` for every new command, defeating the config-driven goal.

Decision: keep the per-language `commands/*.sh` sourced-mapping design, looked up by command name via indirect expansion.

### Edge Cases
- **Duplicate command names across `commands/*.sh` files**: not a problem — silent last-sourced-wins (glob order) is acceptable; no collision detection needed.
- **Mapped script file missing/renamed**: `bin/tingle` raises a regular error (the shell's own "No such file or directory" is fine) rather than failing silently.
- **Mapped script not executable / no shebang**: error — `bin/tingle` invokes scripts directly (`"$path" "$@"`), so every mapped script must be `chmod +x` with a proper shebang; there is no per-language interpreter dispatch.
- **Empty or missing `commands/` directory**: error — the glob loop must not silently no-op on an unexpanded glob pattern; guard with `nullglob` (or an explicit existence/emptiness check) and fail clearly if no command files are found.
- **Args with spaces/special characters**: dispatch preserves them end-to-end via `shift; "$resolved_path" "$@"` — never `eval` or `$*`.

### Testing Strategy
Manual verification by the user for now (per Expected Behavior above). Automated tests are deferred to a future issue.

### Performance & Security
- **Performance**: sourcing all `commands/*.sh` files on every `tingle` invocation is negligible overhead for the expected small number of files; no caching/lazy-loading needed.
- **Security**: `commands/*.sh` files are sourced as trusted shell code, not sandboxed data — anyone who can write to `commands/` can execute arbitrary code via `bin/tingle`. This is the same trust level as the rest of the repo (currently single-committer), so no additional hardening is needed, but this should be documented (e.g. in the repo's README or `docs/agents/architecture.md`) so it stays a conscious, revisited decision if the project ever gains other committers.

### Scope Boundaries
- **In scope**: `bin/check_file_size.py` → `python/check_file_size.py` migration; `bin/tingle` CLI hub; `commands/python.sh` with the `check_file_size` mapping; empty `commands/node.sh` and `commands/shell.sh` scaffolds.
- **Out of scope**: any actual node/shell commands (none exist in the repo today); making `tingle` invocable from any directory via PATH/symlink setup (handled manually by the repo owner, outside this issue).

### Ownership
`commands/` is a new root-level directory. It's tightly coupled to `bin/tingle`'s dispatch logic (the mapping files it sources), so it's owned by the `cli` agent as an extension of its existing `bin/` scope, rather than a new specialist or `architect`. `.claude/agents/cli.md` should be updated to reflect this extended scope as part of this work.

### Repo Conventions To Follow
Per `docs/agents/architecture.md` and `.claude/agents/cli.md`, new entry points/scripts must be registered in the `Scripts` table in `README.md`. This issue should add rows for `tingle` (bin/, shell) and `check_file_size` (python/, moved) to that table.

### Acceptance Criteria
- [ ] `bin/check_file_size.py` moved to `python/check_file_size.py`
- [ ] `bin/tingle` script created and executable (`chmod +x`)
- [ ] `commands/` directory created at repo root
- [ ] `commands/python.sh` created with `check_file_size` mapping
- [ ] `commands/node.sh` and `commands/shell.sh` created as empty scaffolds (no mappings)
- [ ] `tingle check_file_size path/` executes the python script correctly
- [ ] Unknown command prints error + available commands, exits 1
- [ ] No arguments prints usage, exits 1
- [ ] Works from any working directory (TINGLE_FOLDER resolved from script location)
- [ ] `commands/*.sh` trust model (sourced as trusted shell code, not sandboxed) documented in the repo's docs
- [ ] `.claude/agents/cli.md` updated to extend its scope to `commands/`
- [ ] `README.md` Scripts table updated with rows for `tingle` and `check_file_size`

## Benefits
- Single, consistent command interface for all tingle scripts regardless of language
- New commands are added via config (`commands/*.sh`), not by editing `bin/tingle` itself
- Users no longer need to know each script's path or implementation language
