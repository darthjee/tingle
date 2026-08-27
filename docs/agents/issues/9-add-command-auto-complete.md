# Issue: Add command auto complete

## Description
Today `tingle` only supports level-one autocomplete: pressing TAB after `tingle` completes to a top-level command name (e.g. `tingle check_file_size`). This issue adds level-two autocomplete: once a command name is already typed, pressing TAB delegates to that command itself, which decides what its own completions should be.

## Problem
Commands have no way to provide argument/flag-aware completions. The hub only knows command names from `commands/*.json`; it has no contract for asking an individual command what a partial argument should complete to.

## Expected Behavior
- `tingle check_` + TAB completes command names (existing level-one behavior, unchanged).
- `tingle check_file_size <TAB>` delegates to `check_file_size`'s own completion logic. Since `check_file_size` takes files/folders, it gets native file/folder completion for free via a generic fallback — no completion code required in the command itself.
- Commands that need custom completion logic (future commands) can ship a `completion.<ext>` file and the hub will detect and delegate to it automatically.

## Solution

### Flow verb protocol
The first argument passed to every command's entrypoint is always a flow verb, consumed internally by `bin/tingle`/the completion hub and never typed by the user:

```
tingle <cmd> [...args]        -> <cmd>/main.<ext> run [...args]
tingle <cmd> <TAB>            -> <cmd>/main.<ext> complete [...args]
```

This keeps the entrypoint contract uniform and eliminates any chance of the verb colliding with a command's own subcommands/flags — the command's own parser only ever sees `argv[1:]`.

`main.<ext>` becomes a trivial dispatcher, e.g. in Python:

```python
import sys

def main():
    flow = sys.argv[1]      # "run" or "complete"
    args = sys.argv[2:]
    if flow == "complete":
        completion(args)
    else:
        executor(args)
```

### Completion receives raw argv
The completion handler receives the raw argv, including the possibly-empty current word being typed (in bash, `COMP_WORDS[COMP_CWORD]`, empty right after `tingle check_file_size ` + TAB). The hub calls:

```bash
"$main" complete "${COMP_WORDS[@]:2}"   # everything after the command name, including the trailing ""
```

The completion handler must therefore read raw argv directly rather than going through a strict parser (e.g. `argparse` swallows/rejects empty strings) — this must be documented in the contract so the first command built on `argparse` doesn't break silently.

### Refactoring
- **Common entrypoint.** Change each command's entrypoint from `<language>/<command>/<command>.<extension>` to `<language>/<command>/main.<extension>`, which parses the flow verb and delegates to either the executor (`//executor.`) or the completion handler (`//completion.`). Shared files live in `lib` (`<language>/<command>/lib.<extension>`).
- **Feature detection by file presence.** The hub detects completion support by whether `completion.<ext>` exists next to a command's `main.<ext>` — not by probing the command at runtime. If present, delegate; otherwise fall back to the generic behavior below.
- **Generic fallback: native file completion.** Commands that take files/folders (like `check_file_size`) ship no `completion.<ext>` and still get native file/folder completion via `compgen -f` + `compopt -o filenames`. This satisfies `check_file_size`'s completion needs with zero command-specific code.
- **Single source of truth for resolution.** `bin/tingle` exposes a resolution helper (e.g. `tingle resolve <cmd>`), and the completion hub shells out to it instead of duplicating the command-to-script resolution/JSON-parsing/load-order logic.

### check_file_size autocomplete
Since `check_file_size` takes files and folders as arguments, its autocomplete is plain file/folder completion via the generic fallback above — no command-specific completion code needed.

### completions/tingle.bash split
This file is becoming large, so it is split into:
- `completions/tingle.bash`: central hub.
- `completions/bash/tingle.sh`: completion for command names (`tingle check_` + TAB).
- `completions/bash/commands.sh`: completion that delegates to a command's own completion handler (`tingle check_file_size ` + TAB).

### Backward compatibility / migration scope
Today `bin/tingle` execs the resolved `commands/*.json` path directly with the raw args (`exec "$TINGLE_FOLDER/${command_paths[$index]}" "$@"`) — no flow verb prepended. Adopting the flow-verb protocol means `bin/tingle` must unconditionally prepend `run`/`complete` as `argv[1]` for every command it dispatches to, so every existing command's entrypoint must speak the new contract, not just `check_file_size`.

This issue's scope covers migrating **both** existing commands to the new `main.<ext>` / `run`+`complete` contract:
- `check_file_size`: `python/check_file_size/check_file_size.py` -> `python/check_file_size/main.py`, splitting current logic into `//executor.` (existing behavior) and `//completion.` (generic file/folder fallback). `commands/python.json`'s `check_file_size.path` is updated to point at `main.py`.
- `install`: `shell/install.sh` -> `shell/install/main.sh` (or equivalent), wrapping the existing install logic as the `run` executor; no completion needed (falls through to the generic/no-op case) since `install` takes no file/folder arguments. `commands/install.json`'s `install.path` is updated accordingly.

This avoids special-casing old-contract vs. new-contract commands in `bin/tingle`, and avoids leaving `install` broken by an unexpected leading `run` argument once the verb is prepended unconditionally.

### install and the generic fallback
`install` takes no arguments, but it still ships no `completion.<ext>` and simply falls through to the same generic file/folder completion as any other completion-less command — the hub's fallback behavior does not change based on whether a command declares it accepts arguments. Offering (unused) file/folder suggestions after `tingle install <TAB>` is an accepted minor UX quirk, not a functional problem; no per-command "accepts args" flag is introduced in `commands/*.json` for this issue.

### Performance & security
Completion scripts are dispatched with the same trust level as the commands themselves (same repo, same author) and are expected to be fast/local (reading argv, listing files, etc.). No timeout or sandboxing is added for this issue — a command's `completion.<ext>` is trusted the same way its `executor.<ext>` already is.

## Benefits
- Commands can provide rich, context-aware argument/flag completion instead of only top-level command-name completion.
- Uniform `run`/`complete` entrypoint contract removes any risk of the flow verb colliding with a command's own arguments.
- `check_file_size` gets useful file/folder completion for free, with zero command-specific completion code.
- Feature detection by file presence keeps the hub simple and lets future commands opt in to custom completion just by adding a `completion.<ext>` file.
