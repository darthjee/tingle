# Spec: the `php_complexity` config section

Sub-issue: #350 (`details` key added by #351). Parent: #344. Shared
contracts: [README.md](README.md).

`tingle code_check php_complexity` reads its personal defaults from the
`php_complexity` section of `~/.tingle/code_check/config.json`, the file
`file_size`, `rubycritic` and `js_complexity` already use. The rules are
`js_complexity`'s (`python/code_check/js_complexity/config.py`).

## 1. Section

- The file is `code_check.config.default_path()`
  (`~/.tingle/code_check/config.json`, computed at call time).
- The section is loaded with
  `code_check.config.load_section("php_complexity")` through
  `DockerCheck._load_config`. Other sections are ignored. There is no legacy
  section name.
- `python/code_check/php_complexity/config.py` holds `SCHEMA` and
  `validate(section, path)`, built from `code_check.validators` exactly like
  `js_complexity/config.py`: `validate` returns the section unchanged or
  raises `ConfigError(path, reason)` for the first bad key, in the section's
  key order (`code_check.validators.validate_section`). `ConfigError` is
  re-exported from `code_check.config`.

```python
SCHEMA: dict[str, Validator] = {
    "warn": non_negative_number,
    "error": non_negative_number,
    "critical": non_negative_number,
    "top": non_negative_int,
    "exclude": list_of_str,
    "ignore": list_of_str,
    "include": list_of_str,
    "no_default_excludes": boolean,
    "gitignore": boolean,
    "fail_on": one_of(["warn", "error", "critical"], nullable=True),
    "min_level": one_of(["ok", "warn", "error", "critical"]),
    "image": non_empty_str,
    "details": nullable_non_negative_int,   # from #351
}
```

## 2. Keys

| Key | Validator | Reason when invalid | Added by |
|-----|-----------|---------------------|----------|
| `warn` | `non_negative_number` (int or float, finite; booleans rejected) | `'warn' must be a number >= 0` | #350 |
| `error` | `non_negative_number` | `'error' must be a number >= 0` | #350 |
| `critical` | `non_negative_number` | `'critical' must be a number >= 0` | #350 |
| `top` | `non_negative_int` (booleans and floats rejected) | `'top' must be an integer >= 0` | #350 |
| `exclude` | `list_of_str` | `'exclude' must be a list of strings` | #350 |
| `ignore` | `list_of_str` | `'ignore' must be a list of strings` | #350 |
| `include` | `list_of_str` | `'include' must be a list of strings` | #350 |
| `no_default_excludes` | `boolean` | `'no_default_excludes' must be a boolean` | #350 |
| `gitignore` | `boolean` | `'gitignore' must be a boolean` | #350 |
| `fail_on` | `one_of(["warn", "error", "critical"], nullable=True)` | `'fail_on' must be one of warn, error, critical or null` | #350 |
| `min_level` | `one_of(["ok", "warn", "error", "critical"])` | `'min_level' must be one of ok, warn, error or critical` | #350 |
| `image` | `non_empty_str` | `'image' must be a non-empty string` | #350 |
| `details` | `nullable_non_negative_int` | `'details' must be an integer >= 0 or null` | #351 |

- There is **no** `ext` key: `"ext": [".php"]` is reported as
  `unknown key 'ext'`, exit 1, as in `rubycritic` and `js_complexity`.
- Before #351, `details` is an unknown key. #351 adds it to `SCHEMA` and to
  `SINGLE_DEFAULTS` (default `None`).
- `no_default_excludes: true` also turns off the `bootstrap/cache` rule (see
  [selection.md](selection.md#4-skip-rules)). There is no separate key for
  it, and none for the Blade skip, which always applies.
- The thresholds are not compared with each other.

## 3. Precedence

The merge is `DockerCheck._merge`, the same as `js_complexity`'s:

- **Single values** (`warn`, `error`, `critical`, `top`, `fail_on`,
  `min_level`, `image`, and `details` from #351): built-in default < config <
  CLI. A config `null` means unset. The built-in defaults are `20`, `40`,
  `60`, `0`, `null`, `"ok"`, the default image and `null`.
- The default image is only computed (and `shell/linux/VERSION` only read)
  when neither `--image` nor `image` is set.
- **Lists** (`exclude`, `ignore`, `include`): config list first, then the
  CLI list (for `exclude`, the split `--exclude` value), concatenated and
  deduplicated keeping the first occurrence. The default excludes are added
  in front afterwards, unless `no_default_excludes` resolves to true.
- **Booleans:** `no_default_excludes` is
  `--no-default-excludes or config.no_default_excludes (default false)`;
  `gitignore` is `not --no-gitignore and config.gitignore (default true)`.
  The CLI can only turn behaviour off, and it wins over the config.
- **`--no-config`** (added by #350): the file is not read and not validated,
  so the order becomes built-in default < CLI.

When a section was loaded, the header shows `Config: <config file>` (dim).

## 4. Missing file or section

- A missing file is fine: the built-in defaults apply, and no `Config:` line
  is printed.
- A file without a `php_complexity` section is fine too, with the same
  result.
- An empty section (`"php_complexity": {}`) is valid; it loads, so the
  `Config:` line is printed.

### Compatibility (normative)

An existing `~/.tingle/code_check/config.json` with `file_size`,
`rubycritic` and/or `js_complexity` sections stays valid and means exactly
the same after #350: those checks ignore the `php_complexity` section, and
`php_complexity` ignores theirs. A file without a `php_complexity` section
uses the built-in defaults. The new section never makes an existing file
invalid.

## 5. Error handling

Every config error prints `Error: <path>: <reason>` in red on stderr and
exits 1, before any file selection or Docker call. The reasons are
`file_size`'s, `rubycritic`'s and `js_complexity`'s:

| Problem | Reason |
|---------|--------|
| File unreadable | `cannot read file: <OS error>` |
| Invalid JSON | `invalid JSON: <json error>` |
| Top level not an object | `top level must be an object` |
| `php_complexity` not an object | `'php_complexity' must be an object` |
| Unknown key | `unknown key '<key>'` |
| Wrong type or value | the reason from [section 2](#2-keys) |

For example:

```
Error: /home/me/.tingle/code_check/config.json: unknown key 'ext'
Error: /home/me/.tingle/code_check/config.json: 'warn' must be a number >= 0
Error: /home/me/.tingle/code_check/config.json: 'php_complexity' must be an object
```

An invalid `php_complexity` section only breaks `php_complexity`; an invalid
section of another check only breaks that check, as today (each check loads
only its own section).

## 6. Example

```json
{
  "js_complexity": {
    "warn": 40
  },
  "php_complexity": {
    "warn": 25,
    "error": 50,
    "critical": 80.5,
    "top": 20,
    "exclude": ["generated"],
    "no_default_excludes": false,
    "ignore": ["tests/**"],
    "include": ["src/**"],
    "gitignore": true,
    "fail_on": "error",
    "min_level": "warn",
    "image": "darthjee/tingle_php_complexity:0.9.0",
    "details": 5
  }
}
```

With this file, `tingle code_check php_complexity . --warn 30 --exclude
fixtures --ignore '**/legacy/**'` runs with `warn=30` (CLI wins),
`error=50`, `critical=80.5`, excludes `generated, fixtures` on top of the 16
defaults (and the `bootstrap/cache` rule), ignore globs
`tests/**, **/legacy/**`, the image from the config, and `--details 5`
behaviour (from #351). The `js_complexity` section has no effect on it.

## 7. Docs and tests

#350 updates, in the same PR:

- `long_help` in `commands/python.json` (the config file, its keys and
  `--no-config`) and the executor module docstring;
- the `php_complexity` row of the "Configuration file" table in
  `docs/guides/code_check.md`, and
  `docs/guides/code_check/php_complexity.md`;
- tests under `python/tests/code_check/php_complexity/`, covering every
  key's valid and invalid values (booleans as numbers, `NaN`, negative
  numbers, an empty `image`, `ext`, `details` before #351), each precedence
  rule, list merging and deduplication, `--no-config` with a broken file, a
  missing file, a missing section, an empty section, `php_complexity` not an
  object, `image` from the config avoiding the `VERSION` read,
  `no_default_excludes: true` dropping the `bootstrap/cache` rule but not
  the Blade skip, and a file with only `file_size`/`rubycritic`/
  `js_complexity` sections loading the defaults.

#351 adds the `details` key, its tests and its docs.
