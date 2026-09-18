# Issue: Codacy: names appears unused. Verify use (or export if used externally) (completions/bash/tingle.sh:14)

## Description
Codacy's shellcheck analysis (rule `SC2034`) flags the local variable `names` declared in `_tingle_complete_command_names()` (`completions/bash/tingle.sh:14`) as unused.

## Problem
The function's `local` declaration on line 14 includes `names` alongside `tingle_folder commands_dir cmd_file cmd_files names cur`, but the function never assigns to or reads `names` anywhere in its body. The actual collected command names are accumulated in the separately declared `command_names` array (line 32), so `names` is dead code left over from an earlier version of the function.

## Expected Behavior
Shellcheck (via Codacy) should report no unused-variable warnings for `completions/bash/tingle.sh`, and the completion function should behave identically to today (no functional change).

## Solution
Remove `names` from the `local` declaration on line 14 of `completions/bash/tingle.sh`, leaving `tingle_folder commands_dir cmd_file cmd_files cur`. No other changes are needed — the variable is not referenced elsewhere in the file.

## Benefits
- Resolves the Codacy/shellcheck SC2034 warning.
- Removes dead code, making the function easier to read.
