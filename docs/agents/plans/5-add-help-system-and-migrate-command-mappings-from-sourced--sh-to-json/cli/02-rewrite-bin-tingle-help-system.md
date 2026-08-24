# Rewrite bin/tingle's help system

Rewrite `bin/tingle` to load commands from `commands/*.json` via `jq`
instead of sourcing `commands/*.sh`, and add the full help contract agreed
on the issue:

- Load every `commands/*.json` file in glob (alphabetical) order:
  `node.json`, `python.json`, `shell.json`. Build a name → `{path,
  short_help, long_help}` table; on a name collision across files, the
  first file that defined the name wins — do not overwrite it, and do not
  treat this as an error.
- If any `commands/*.json` file fails to parse as valid JSON (`jq` returns
  a non-zero exit code on it), print a clear error naming the bad file to
  stderr and exit non-zero immediately — do not dispatch with partial data.
- If a command entry is missing `short_help` or `long_help`, substitute a
  placeholder (e.g. `(no description)`) for the missing field wherever it
  would be shown.
- `tingle`, `tingle help`, and `tingle --help` (all three, no args after
  `help`/`--help`) print the general help and exit `0`:

  ```
  Usage: tingle <command> [args...]

  Commands:
    <name>        <short_help>
    ...
  ```

  Commands are listed in the same load order used for name resolution.
- `tingle --help <command>` prints `<command>`'s `long_help` and exits `0`.
  Any arguments after `<command>` are ignored.
- An unknown command (first arg doesn't match any loaded command name, and
  isn't `help`/`--help`) prints `Error: command '<x>' not found.` followed
  by the same formatted `name  short_help` listing used by the general
  help, and exits non-zero — same as today, but replacing the old flat
  `Available commands: a,b,c` line.
- A registered command whose `path` doesn't exist on disk is **not**
  validated at load time or in `--help`/listing output — it only surfaces
  when that specific command is dispatched and `exec` fails, same as
  today's implicit behavior.
- Preserve the existing dispatch behavior for a valid, known command:
  resolve its `path` and `exec` it with the remaining arguments.

## Files to Change

- `bin/tingle` — replace the `.sh`-sourcing/`${!1}`-indirection logic with
  `jq`-based JSON loading, and add the `--help`/`help` handling described
  above.
