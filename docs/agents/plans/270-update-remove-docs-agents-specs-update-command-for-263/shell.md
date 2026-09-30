# Shell Plan: update: remove docs/agents/specs/update_command/ for #263

Main plan: [plan.md](plan.md)

## Shared contracts

- Exit codes: after the executor `exec`s the installer, the exit status is
  the installer's own. Exit 0 means completed, checked, or already up to
  date. Everything else is non-zero.
- The git-checkout path is the #268 one.

## Implementation Steps

### Step 1 — Fix the shell/update/executor.sh header comment
Comments only, with no code change:
- Replace "0 – Handed off successfully" (around :78) with the real rule:
  after the `exec`, the exit status is the installer's. List the
  installer's non-zero cases too: edited files without `--force`, and a
  lock held by another run (README.md:211).
- Step 5: say `install/installer.sh` must exist **and be executable**
  (matching the code at around :466).
- Say that network, rate-limit (403/429) and unexpected-response errors
  print a hint to pin a version (update-command.md:126-128).
- Say that a missing `.sha256` or a hash mismatch aborts and deletes the
  download (update-command.md:158-160).
- Say that `GITHUB_TOKEN` is not supported (update-command.md:130,
  README.md:179). Today only the code comment at :301 says it.

## Files to Change
- `shell/update/executor.sh`: header comment only.

## CI Checks
- No CI job covers shell comments. Run `bash -n shell/update/executor.sh`
  as a sanity check.

## Notes
- `main.sh` is a plain dispatcher and needs no change.
