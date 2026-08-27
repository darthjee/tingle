# Plan: Add command auto complete

Issue: [9-add-command-auto-complete.md](../../issues/9-add-command-auto-complete.md)

## Overview

Add level-two (command-argument) tab completion to `tingle`. Every command's
entrypoint moves from `<language>/<command>/<command>.<ext>` to a uniform
`<language>/<command>/main.<ext>`, which dispatches on a leading `run`/`complete`
flow verb to either the command's executor or its completion handler. The
completion hub (`completions/`) is split into a central dispatcher plus two
dedicated files, gains a generic native file/folder fallback for commands
without their own completion logic, and resolves commands through a new
`tingle resolve <cmd>` helper instead of re-parsing `commands/*.json` itself.
Both existing commands (`check_file_size`, `install`) are migrated to the new
contract so `bin/tingle` can prepend the flow verb unconditionally, with no
special-casing of old-vs-new-contract commands.

## Agents involved

- [python](python.md)
- [shell](shell.md)
- [cli](cli.md)
- [product-owner](product-owner.md)

## Shared contracts

1. **Flow verb protocol.** `cli` invokes every command as `<dir>/main.<ext> run [...args]` (normal execution) or `<dir>/main.<ext> complete [...args]` (tab completion). The verb is argv[1]; the command's own args are argv[2:]. `python` and `shell` implement `main.<ext>` as a thin dispatcher reading `sys.argv[1]`/`$1` for the verb.

2. **Entry point path convention.** `commands/*.json`'s `path` field (owned by `cli`) must point at the new `main.<ext>` files once `python`/`shell` create them:
   - `check_file_size` → `python/check_file_size/main.py`
   - `install` → `shell/install/main.sh`

3. **Completion is opt-in per command.** `cli`'s hub detects completion support by checking whether `completion.<ext>` exists next to a command's `main.<ext>` — it never invokes `main.<ext> complete` to probe. Neither `check_file_size` nor `install` ships a `completion.<ext>` in this issue; both fall through to the hub's generic native file/folder fallback (`compgen -f` + `compopt -o filenames`), including for `install` (which takes no args) — this is an accepted minor UX quirk, not a bug, per the issue's decision.

4. **Raw argv contract for completion handlers.** If/when a command does add `completion.<ext>`, it receives raw argv — including a possibly-empty trailing element for the word being typed — and must not parse it with a strict parser like `argparse`, since `cli` calls `"$main" complete "${COMP_WORDS[@]:2}"` verbatim, trailing empty string included. (No command in this issue implements `completion.<ext>`; this contract only needs to be documented, by `product-owner`, for future commands.)

5. **Resolution helper.** `cli` exposes `tingle resolve <cmd>`, printing the absolute path to that command's `main.<ext>` (or exiting non-zero for an unknown command). `cli`'s own `completions/bash/commands.sh` is the sole consumer in this issue, calling it instead of re-parsing `commands/*.json`.
