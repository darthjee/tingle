# Spec: the `rubycritic` config section

Sub-issue: #297. Parent: #290. Shared contracts: [README.md](README.md).

`tingle code_check rubycritic` reads its personal defaults from the
`rubycritic` section of `~/.tingle/code_check/config.json`, the file
`file_size` already uses. This follows `python/code_check/file_size/config.py`
and `python/code_check/config.py`.

## 1. Section

- The file is `code_check.config.default_path()`
  (`~/.tingle/code_check/config.json`, computed at call time).
- The section is loaded with `code_check.config.load_section("rubycritic")`.
  Other sections (`file_size`, ...) are ignored. There is no legacy section
  name.
- `python/code_check/rubycritic/config.py` holds `SCHEMA` and
  `validate(section, path)`, with the same structure as `file_size`'s:
  `validate` returns the section unchanged or raises `ConfigError(path,
  reason)` for the first bad key, in the section's key order.
- The validators that already exist in `file_size/config.py` are reused, not
  copied. Moving them to a shared module (for example `code_check/config.py`)
  is allowed, as long as `file_size`'s messages and behaviour stay the same.

## 2. Keys

| Key | Validator | Reason when invalid |
|-----|-----------|---------------------|
| `warn` | number ≥ 0: a JSON int or float, finite; `true`/`false` rejected | `'warn' must be a number >= 0` |
| `error` | same | `'error' must be a number >= 0` |
| `critical` | same | `'critical' must be a number >= 0` |
| `top` | int ≥ 0; booleans and floats rejected (`file_size`'s `_non_negative_int`) | `'top' must be an integer >= 0` |
| `exclude` | list of strings (empty list allowed) | `'exclude' must be a list of strings` |
| `ignore` | list of strings | `'ignore' must be a list of strings` |
| `include` | list of strings | `'include' must be a list of strings` |
| `no_default_excludes` | boolean | `'no_default_excludes' must be a boolean` |
| `gitignore` | boolean | `'gitignore' must be a boolean` |
| `fail_on` | `"warn"`, `"error"`, `"critical"` or `null` | `'fail_on' must be one of warn, error, critical or null` |
| `min_level` | `"ok"`, `"warn"`, `"error"` or `"critical"` | `'min_level' must be one of ok, warn, error or critical` |
| `image` | a string that is not empty after trimming whitespace | `'image' must be a non-empty string` |

- There is **no** `ext` key. `"ext": [".rb"]` is an unknown key.
- Python's `json` accepts `NaN` and `Infinity`; they are rejected for
  `warn`/`error`/`critical` ("finite").
- The thresholds are not checked against each other, as in `file_size`.

## 3. Precedence

The merge mirrors `CheckFileSize._merge`:

- **Single values** (`warn`, `error`, `critical`, `top`, `fail_on`,
  `min_level`, `image`): built-in default < config < CLI. A flag given on the
  CLI always wins. The built-in defaults are `100`, `200`, `400`, `0`,
  `null`, `"ok"` and `darthjee/tingle_rubycritic:<tingle version>`.
- The default image is only computed (and `shell/linux/VERSION` only read)
  when neither `--image` nor `image` is set, so a config `image` avoids the
  version-file error.
- **Lists** (`exclude`, `ignore`, `include`): config list first, then the CLI
  list (for `exclude`, the comma-separated `--exclude` value split and
  trimmed), concatenated and deduplicated keeping the first occurrence. The
  CLI never replaces a config list. The default excludes are added in front
  afterwards, unless `no_default_excludes` resolves to true.
- **Booleans:** `no_default_excludes` resolves to
  `--no-default-excludes or config.no_default_excludes (default false)`.
  `gitignore` resolves to
  `not --no-gitignore and config.gitignore (default true)`. The CLI can only
  turn behaviour off, and it wins over the config.
- **`--no-config`:** the file is not read and not validated, so the order
  becomes built-in default < CLI. The `--no-config` flag is added by #297.

When a section was loaded, the report header shows
`Config: <config file>` (dim), as in `file_size` (see
[subcommand.md](subcommand.md#6-report)).

## 4. Missing file or section

- A missing file is fine: the built-in defaults apply, and no `Config:` line
  is printed.
- A file without a `rubycritic` section is fine too, with the same result.
- An empty section (`"rubycritic": {}`) is valid; it loads, so the `Config:`
  line is printed.

## 5. Error handling

Every config error prints `Error: <path>: <reason>` in red on stderr and
exits 1, before any file selection or Docker call. The reasons reuse
`file_size`'s wording:

| Problem | Reason (from `code_check.config` or `validate`) |
|---------|--------------------------------------------------|
| File unreadable | `cannot read file: <OS error>` |
| Invalid JSON | `invalid JSON: <json error>` |
| Top level not an object | `top level must be an object` |
| `rubycritic` not an object | `'rubycritic' must be an object` |
| Unknown key | `unknown key '<key>'` |
| Wrong type or value | the reason from [section 2](#2-keys) |

For example:

```
Error: /home/me/.tingle/code_check/config.json: unknown key 'ext'
Error: /home/me/.tingle/code_check/config.json: 'warn' must be a number >= 0
```

## 6. Example

```json
{
  "file_size": {
    "warn": 250
  },
  "rubycritic": {
    "warn": 100,
    "error": 200,
    "critical": 400.5,
    "top": 20,
    "exclude": ["db"],
    "no_default_excludes": false,
    "ignore": ["spec/fixtures/**"],
    "include": ["app/**", "lib/**"],
    "gitignore": true,
    "fail_on": "error",
    "min_level": "warn",
    "image": "darthjee/tingle_rubycritic:0.6.0"
  }
}
```

With this file, `tingle code_check rubycritic . --warn 50 --exclude tmp2
--ignore '**/legacy/**'` runs with `warn=50` (CLI wins), `error=200`,
`critical=400.5`, excludes `db, tmp2` on top of the defaults, ignore globs
`spec/fixtures/**, **/legacy/**`, and the image from the config.

## 7. Docs and tests

Issue #297 updates, in the same PR:

- `long_help` in `commands/python.json` (the config file and `--no-config`)
  and the executor module docstring;
- the `rubycritic` row of the "Configuration file" table and the
  `rubycritic` section of `docs/guides/code_check.md`;
- tests under `python/tests/code_check/rubycritic/`, covering every key's
  valid and invalid values (booleans as numbers, `NaN`, negative numbers,
  empty `image`, `ext`), each precedence rule, list merging and
  deduplication, `--no-config` with a broken file, a missing file, a missing
  section, an empty section, and `image` from the config avoiding the
  `VERSION` read.
