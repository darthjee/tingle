# Parse arguments and detect the install
**Arguments:** loop over `"$@"`: `--check` and `--force` set flags. One
positional argument is the pin. An unknown `-*` option or a second positional
argument prints a usage error and exits non-zero. The pin is the positional
argument if given, else `${TINGLE_VERSION:-}`.

**Detect the install (spec 3.1, E3, E14, E11):** print
`Updating tingle in <TINGLE_FOLDER>` first. Then:

- `<folder>/tingle.json` exists: it must pass `tingle_json_check`, otherwise
  report a corrupt `tingle.json` and exit non-zero. Read `version` and `repo`
  with `jq -r`.
- No `tingle.json` and `<folder>/.git` exists (file or dir): say it is a git
  checkout and should be updated with `git pull`, and exit non-zero.
- Neither: explain tingle can't tell how it was installed, and exit non-zero.
- The folder isn't writable (`[ -w ]`): fail and name the folder.

## Files to Change
- `shell/update/executor.sh` — argument parsing and install detection.
