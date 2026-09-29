# Spec: config file `~/.tingle/code_check/config.json`

Sub-issue: #253. Shared contracts: [README.md](README.md) (flags, config keys,
precedence, exit codes).

## Behaviour

- Location: `$HOME/.tingle/code_check/config.json` (`Path.home()`). There is
  no flag to change it, and no project-level config (out of scope).
- The top level is a JSON object. The `check_file_size` key holds this
  command's options. Other top-level keys are ignored, because they are
  reserved for the future `code_check` tool.
- Schema of the `check_file_size` section (every key is optional):

  | Key | Type | CLI flag |
  |-----|------|----------|
  | `warn`, `error`, `critical` | int ≥ 0 | `--warn`, `--error`, `--critical` |
  | `top` | int ≥ 0 | `--top` |
  | `exclude` | list of str | `--exclude` (comma-separated on the CLI) |
  | `no_default_excludes` | bool | `--no-default-excludes` |
  | `ignore` | list of str | `--ignore` |
  | `include` | list of str | `--include` |
  | `ext` | list of str | `--ext` |
  | `gitignore` | bool (default `true`) | `--no-gitignore` (inverted) |
  | `fail_on` | `"warn"`, `"error"`, `"critical"` or `null` | `--fail-on` |
  | `min_level` | `"ok"`, `"warn"`, `"error"` or `"critical"` | `--min-level` |

- Merge rules (README section 4): single values follow built-in defaults <
  config < CLI. Lists from the config and the CLI are concatenated,
  deduplicated, and keep their order. The CLI `--no-*` flags can only turn
  behaviour off.
- A **missing file** or a **missing `check_file_size` section** is fine: the
  built-in defaults are used, with no output.
- `--no-config` (`store_true`, no config key): the config file is not read or
  validated at all, so even a broken config is ignored.
- Header: when a `check_file_size` section was loaded (the file exists and
  has the key, even with an empty object), a dim `Config: <config path>` line
  is printed right after the `Thresholds:` line, before the blank line. There
  is no such line when the file or the section is missing, or with
  `--no-config`.
- Errors print `Error: <config path>: <reason>` on stderr and exit **1**,
  before any analysis output:
  - the file is not valid JSON, or cannot be read;
  - the top level is not an object;
  - the `check_file_size` section is not an object;
  - an unknown key (`unknown key 'wran'`);
  - a wrong type or value (`'top' must be an integer >= 0`,
    `'fail_on' must be one of warn, error, critical or null`).

## Examples

```json
{
  "check_file_size": {
    "warn": 200,
    "exclude": ["fixtures"],
    "ignore": ["*.test.js"],
    "fail_on": "error"
  }
}
```

| Invocation | Result |
|------------|--------|
| `tingle check_file_size .` | warn=200, excludes = defaults + `fixtures`, ignores `*.test.js`, gate at `error`. |
| `tingle check_file_size . --warn 400` | warn=400 (CLI wins). |
| `tingle check_file_size . --ignore '*.spec.js'` | Ignores `*.test.js` **and** `*.spec.js`. |
| `tingle check_file_size . --fail-on critical` | Gate at `critical`. |
| `tingle check_file_size . --no-config` | Built-in defaults only; the config is not read, and there is no `Config:` line. |

Header with the config above:

```text
Thresholds: warn=200 | error=500 | critical=1000
Config: /home/user/.tingle/code_check/config.json

...
```

## Edge cases

- JSON booleans are not integers: `"top": true` is a type error, even though
  Python's `bool` is a subclass of `int`.
- `"fail_on": null` means "no gate". The CLI `--fail-on` still overrides it.
- `"gitignore": false` in the config, with no CLI flag, disables `.gitignore`.
  There is no CLI flag to turn it back on (README section 4).
- Empty lists are valid and add nothing.
- The config is validated even when every value is also given on the CLI.
- `path` is not a config key (unknown key → error).
- `tingle check_file_size` with no arguments still prints help and exits 0,
  without reading the config.
- `"check_file_size": {}` is valid: nothing changes, but the `Config:` line is
  printed, because a section was loaded.
- `--no-config` with an invalid config file: no error, built-in defaults.
- Threshold ordering (for example `warn` > `error`) is **not** checked. This
  is out of scope, for the config and for the CLI alike.

## Technical decisions

- New module `python/check_file_size/config.py`:
  - `load_section(name: str, path: Path | None = None) -> dict | None` reads
    the file (default `Path.home() / ".tingle" / "code_check" / "config.json"`,
    computed at call time so a changed `HOME` applies) and returns the named
    section, or `None` when the file or section is missing. Returning `None`
    instead of `{}` lets the executor tell "no section" from "empty section"
    for the `Config:` header line. It knows nothing about `check_file_size`
    keys, so `code_check` can reuse it.
  - It raises `ConfigError(path, reason)` for the file-level errors (bad JSON,
    unreadable file, non-object top level or section).
  - Key and type validation for `check_file_size` lives next to the schema:
    a `SCHEMA` mapping of key → validator in `config.py`, applied by
    `validate(section: dict, path: Path) -> dict`, which raises `ConfigError`
    too and returns the section unchanged.
  - `str(ConfigError(path, reason))` is `"<path>: <reason>"`.
- Merging happens in `executor.py` after argparse, in one method, e.g.
  `_merge(cli: dict, config: dict) -> dict`. Single-value flags default to
  `None` in `FLAGS` so "not passed" can be detected, and the built-in
  defaults (`Constants.DEFAULT_*`, `top=0`, `min_level="ok"`) are applied
  after merging.
- `executor.py` catches `ConfigError`, prints it in red with
  `Palette(sys.stderr)`, and exits 1, the same as "path not found".
- With `--no-config`, `executor.py` skips `load_section` and `validate`
  entirely and merges with no config.
- The `Config:` line is printed by the executor/reporter only when
  `load_section` returned a dict (not `None`).

## Tests expected

- `python/tests/check_file_size/test_config.py` (new), using a temporary
  `HOME` (`monkeypatch.setenv("HOME", tmp_path)`) or an explicit `path`:
  missing file → `None`; missing section → `None`; empty section → `{}`;
  other sections ignored; bad
  JSON, non-object top level or section, unknown key, and each wrong type or
  value (including bool as int) → `ConfigError`.
- `test_executor.py`: config single values apply; CLI overrides them; lists
  are merged and deduplicated; `gitignore: false` and `no_default_excludes:
  true` apply; a config error prints to stderr and exits 1 with no stdout
  report; `--no-config` ignores a valid config and also an invalid one (no
  error); the `Config: <path>` line appears when a section (even an empty one)
  was loaded, and not when the file or section is missing or with
  `--no-config`.
