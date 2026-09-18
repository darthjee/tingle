# Plan: Codacy: names appears unused. Verify use (or export if used externally) (completions/bash/tingle.sh:14)

Issue: [64-codacy-names-appears-unused-verify-use-or-export-if-used-externally-completions-bash-tingle-sh-14.md](../issues/64-codacy-names-appears-unused-verify-use-or-export-if-used-externally-completions-bash-tingle-sh-14.md)

## Overview
Remove the dead `names` local variable from `_tingle_complete_command_names()` in `completions/bash/tingle.sh` to resolve the Codacy/shellcheck `SC2034` warning. No behavioral change — the function's actual output is built via the separately declared `command_names` array.

## Context
Codacy flagged line 14's `local` declaration (`local tingle_folder commands_dir cmd_file cmd_files names cur`) because `names` is never assigned or read anywhere in the function body.

## Implementation Steps

### Step 1 — Drop the unused `names` local
Edit `completions/bash/tingle.sh:14` to remove `names` from the `local` declaration, leaving `tingle_folder commands_dir cmd_file cmd_files cur`.

## Files to Change
- `completions/bash/tingle.sh` — remove unused `names` from the `local` declaration on line 14.

## Notes
- Purely a dead-code removal; verify manually (or via `shellcheck completions/bash/tingle.sh`) that no other unused variables remain nearby.
