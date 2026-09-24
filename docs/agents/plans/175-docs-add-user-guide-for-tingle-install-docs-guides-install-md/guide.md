# Guide Plan: docs: add user guide for tingle install (docs/guides/install.md)

Main plan: [plan.md](plan.md)

## Overview
Write `docs/guides/install.md` for end users. Then turn the `install`
placeholder in `docs/guides/README.md` into a real link.

## Context
- The command is registered in `commands/shell.json` (`install`).
  `shell/install/main.sh` handles the `run` verb and `exec`s
  `shell/install/executor.sh`, which does the real work.
- `executor.sh` behaviour (the guide's source of truth):
  - Resolves `TINGLE_FOLDER` as the repo root (two levels above the script).
  - Creates `~/.bashrc` if it doesn't exist.
  - If `~/.bashrc` already contains `# >>> tingle >>>`, prints
    `tingle is already installed in <HOME>/.bashrc` and exits 0 without
    changing anything.
  - Otherwise appends a blank line and then this block:
    ```
    # >>> tingle >>>
    export PATH="<TINGLE_FOLDER>/bin:$PATH"
    source "<TINGLE_FOLDER>/completions/tingle.bash"
    # <<< tingle <<<
    ```
    It then prints
    `tingle installed. Run 'source <HOME>/.bashrc' or restart your shell to start using it.`
- The web installer (`install/bootstrap.sh`, described in the root README's
  Installation section) unpacks tingle to `~/.tingle` and runs
  `tingle install` as its last step.
- Completion needs `jq`, which `bin/tingle` requires anyway.

## Implementation Steps

### Step 1 — Write `docs/guides/install.md`
Write for end users, with these sections:
1. **What it does**: one paragraph. It wires tingle into your bash shell by
   adding a marker block to `~/.bashrc`, which puts `bin/` on `PATH` and
   enables `tingle <TAB>` completion.
2. **When to run it**: the web installer already runs it, so link to
   `../../README.md#installation`. For a manually cloned repo, `tingle` is
   not on `PATH` yet, so run `./bin/tingle install` from the repo root the
   first time.
3. **Usage**: `tingle install` (it takes no options).
4. **What it changes**: show the exact block with a placeholder path. Say
   that `~/.bashrc` is created if it is missing, and that nothing else in
   the file is touched.
5. **Running it again**: it is safe. It detects the marker, prints the
   "already installed" message and changes nothing.
6. **Check that it worked**: run `source ~/.bashrc` or open a new shell, run
   `tingle` to see the command list, then try `tingle <TAB>`.
7. Mention prerequisites briefly: bash, plus `jq` for `bin/tingle` and
   completion.

Document only current behaviour. Do not describe moved-repo handling,
uninstall or other shells. Those are tracked in #180 and must not be
promised.

### Step 2 — Link it from the guides index
In `docs/guides/README.md`, replace the `install` placeholder line with a
link and drop *(guide coming soon)*:
`- [\`install\`](install.md) — Install tingle onto PATH and enable bash completion.`

## Files to Change
- `docs/guides/install.md` — new end-user guide.
- `docs/guides/README.md` — turn the `install` entry into a link.

## Notes
- Keep the wording consistent with the `long_help` in `commands/shell.json`.
- The root `README.md` link is the architect's job (see [plan.md](plan.md)).
  Do not edit it here.
- There are no CI checks for markdown under `docs/guides/`.
