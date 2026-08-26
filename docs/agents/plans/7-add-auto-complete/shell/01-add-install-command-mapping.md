# Add install command mapping

Register `install` as a dispatched command, the same way `check_file_size` is registered in `commands/python.json`. This keeps `bin/tingle` a thin dispatcher — no special-casing for `install` inside `bin/tingle` (unlike `help`/`--help`, which are already special-cased and must stay untouched).

## Files to Change

- `commands/shell.json` — currently `{}`; add an `install` key pointing at the new `shell/install.sh`, with `short_help`/`long_help` describing what `tingle install` does (adds `tingle` to `PATH` and installs bash completion via `~/.bashrc`, idempotently).
