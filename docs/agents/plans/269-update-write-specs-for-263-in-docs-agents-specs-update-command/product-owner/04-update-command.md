# Write update-command.md (#266)
Create `docs/agents/specs/update_command/update-command.md`, linking #266.
It covers:
- **CLI:** `tingle update [--check] [--force] [<version>]`, `TINGLE_VERSION`,
  `TINGLE_ASSUME_YES`. Include example sessions (up to date, `--check` with
  edited files, a pin, a refused pin).
- **Flow**, in order:
  1. Detect the install: `tingle.json` present, or a git checkout
     (`git pull` message, non-zero), or unknown (non-zero). Also E3 and E14.
  2. Resolve the target: the GitHub API `releases/latest` via `jq`, or a pin
     that skips the API. Validation (E6) and the floor (E2). Errors (E7, E8,
     E10).
  3. The up-to-date no-op, or `--check` output, including `unknown → X` (E4).
  4. The y/N prompt on `/dev/tty`, or `TINGLE_ASSUME_YES`, or abort without
     a TTY.
  5. Download the zip and `.sha256`, verify, and unzip (E9, E9b), with the
     test hooks.
  6. `exec` the unpacked installer with the env vars set (S1): no trap and
     nothing after it.
- **Rejected alternatives:** the command doing everything itself, re-running
  `bootstrap.sh`, wipe-and-reinstall, scraping the redirect, and
  `releases/latest/download`. No `GITHUB_TOKEN`.
- **Layout:** `shell/update/main.sh` + `executor.sh` (the flow-verb layout of
  `shell/install/`), and the `update` entry in `commands/shell.json`.
- **Testing:** the scenarios from #266, using the test hooks with local zips.
- **Permanent home:** the header comment of `shell/update/executor.sh` (flow
  and test-only hooks), `long_help` in `commands/shell.json` (CLI), and
  `docs/guides/update.md` (#267).

## Files to Change
- `docs/agents/specs/update_command/update-command.md`: new.
