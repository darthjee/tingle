# Restructure detection so the git path runs first
Today `shell/update/executor.sh` does three things, in this order, before it detects the install: it checks for `curl`/`unzip`/`jq`, validates the pin with `validate_version`, and sources `install/manifest.sh`. On a git checkout, that means a pin with a bad format would fail with "invalid version" instead of the git-specific refusal, and a missing `unzip` would block a `git pull`.

Reorder the script like this:
1. Parse arguments (unchanged). Resolve `PIN` from the argument or `TINGLE_VERSION` (unchanged).
2. Print `Updating tingle in <folder>` (unchanged).
3. Detect the install kind: `tingle.json` present means the web path, and otherwise `.git` present means the git path. Neither is still refused with the existing message. `tingle.json` still wins when both exist.
4. On the git path, call a `git_update` function (step 02), which never returns: it exits or `exec`s.
5. The web path then does exactly what it does today, in the same order relative to itself: tool check, pin validation, `tingle_json_check`, writability, and so on. Moving the tool check and pin validation below detection must not change any web-path output. The only difference is that the `Updating tingle in` line now comes before a pin-format error, and the plan accepts that. The `manifest.sh` source can stay at the top, because the file exists in git checkouts too.

## Files to Change
- `shell/update/executor.sh` — move the tool check and pin validation into the web path; add the git branch that dispatches to `git_update`.
