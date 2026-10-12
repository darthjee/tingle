# Spec: the `js_complexity` config section

Sub-issue: #322 (`details` key added by #325). Parent: #315. Shared
contracts: [README.md](README.md).

`tingle code_check js_complexity` reads its personal defaults from the
`js_complexity` section of `~/.tingle/code_check/config.json`, the file
`file_size` and `rubycritic` already use. The rules are `rubycritic`'s
(`python/code_check/rubycritic/config.py`).

## 1. Section

- The file is `code_check.config.default_path()`
  (`~/.tingle/code_check/config.json`, computed at call time).
- The section is loaded with `code_check.config.load_section("js_complexity")`
  through `DockerCheck._load_config` (see
  [docker-check.md](docker-check.md#26-executor-scaffolding-executorpy)).
  Other sections are ignored. There is no legacy section name.
- `python/code_check/js_complexity/config.py` holds `SCHEMA` and
  `validate(section, path)`, built from `code_check.validators` exactly like
  `rubycritic/config.py`: `validate` returns the section unchanged or raises
  `ConfigError(path, reason)` for the first bad key, in the section's key
  order. `ConfigError` is re-exported from `code_check.config`.

## 2. Keys

| Key | Validator | Reason when invalid | Added by |
|-----|-----------|---------------------|----------|
| `warn` | `non_negative_number` (int or float, finite; booleans rejected) | `'warn' must be a number >= 0` | #322 |
| `error` | `non_negative_number` | `'error' must be a number >= 0` | #322 |
| `critical` | `non_negative_number` | `'critical' must be a number >= 0` | #322 |
| `top` | `non_negative_int` (booleans and floats rejected) | `'top' must be an integer >= 0` | #322 |
| `exclude` | `list_of_str` | `'exclude' must be a list of strings` | #322 |
| `ignore` | `list_of_str` | `'ignore' must be a list of strings` | #322 |
| `include` | `list_of_str` | `'include' must be a list of strings` | #322 |
| `no_default_excludes` | `boolean` | `'no_default_excludes' must be a boolean` | #322 |
| `gitignore` | `boolean` | `'gitignore' must be a boolean` | #322 |
| `fail_on` | `one_of(["warn", "error", "critical"], nullable=True)` | `'fail_on' must be one of warn, error, critical or null` | #322 |
| `min_level` | `one_of(["ok", "warn", "error", "critical"])` | `'min_level' must be one of ok, warn, error or critical` | #322 |
| `image` | `non_empty_str` | `'image' must be a non-empty string` | #322 |
| `details` | `nullable_non_negative_int` | `'details' must be an integer >= 0 or null` | #325 |

- There is **no** `ext` key: `"ext": [".js"]` is reported as
  `unknown key 'ext'`, exit 1, as in `rubycritic`.
- Before #325, `details` is an unknown key. #325 adds it to `SCHEMA` and to
  `SINGLE_DEFAULTS` (default `None`).
- `no_default_excludes: true` also turns off the minified skip from #323
  (see [file-selection.md](file-selection.md#4-minified-bundles)). There is
  no separate key for it.
- The thresholds are not compared with each other.

## 3. Precedence

The merge is `DockerCheck._merge`, the same as `rubycritic`'s:

- **Single values** (`warn`, `error`, `critical`, `top`, `fail_on`,
  `min_level`, `image`, and `details` from #325): built-in default < config <
  CLI. A config `null` means unset. The built-in defaults are `50`, `60`,
  `75`, `0`, `null`, `"ok"`, the default image and `null`.
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
- **`--no-config`** (added by #322): the file is not read and not validated,
  so the order becomes built-in default < CLI.

When a section was loaded, the header shows `Config: <config file>` (dim).

## 4. Missing file or section

- A missing file is fine: the built-in defaults apply, and no `Config:` line
  is printed.
- A file without a `js_complexity` section is fine too, with the same
  result.
- An empty section (`"js_complexity": {}`) is valid; it loads, so the
  `Config:` line is printed.

### Compatibility (normative)

An existing `~/.tingle/code_check/config.json` with `file_size` and/or
`rubycritic` sections stays valid and means exactly the same after #322:
`file_size` and `rubycritic` ignore the `js_complexity` section, and
`js_complexity` ignores theirs. A file without a `js_complexity` section
uses the built-in defaults. The new section never makes an existing file
invalid.

## 5. Error handling

Every config error prints `Error: <path>: <reason>` in red on stderr and
exits 1, before any file selection or Docker call. The reasons are
`file_size`'s and `rubycritic`'s:

| Problem | Reason |
|---------|--------|
| File unreadable | `cannot read file: <OS error>` |
| Invalid JSON | `invalid JSON: <json error>` |
| Top level not an object | `top level must be an object` |
| `js_complexity` not an object | `'js_complexity' must be an object` |
| Unknown key | `unknown key '<key>'` |
| Wrong type or value | the reason from [section 2](#2-keys) |

For example:

```
Error: /home/me/.tingle/code_check/config.json: unknown key 'ext'
Error: /home/me/.tingle/code_check/config.json: 'warn' must be a number >= 0
```

An invalid `js_complexity` section only breaks `js_complexity`; an invalid
`rubycritic` section only breaks `rubycritic`, as today (each check loads
only its own section).

## 6. Example

```json
{
  "rubycritic": {
    "warn": 100
  },
  "js_complexity": {
    "warn": 50,
    "error": 60,
    "critical": 75.5,
    "top": 20,
    "exclude": ["generated"],
    "no_default_excludes": false,
    "ignore": ["**/*.test.ts"],
    "include": ["src/**"],
    "gitignore": true,
    "fail_on": "error",
    "min_level": "warn",
    "image": "darthjee/tingle_js_complexity:0.9.0",
    "details": 5
  }
}
```

With this file, `tingle code_check js_complexity . --warn 40 --exclude fixtures
--ignore '**/legacy/**'` runs with `warn=40` (CLI wins), `error=60`,
`critical=75.5`, excludes `generated, fixtures` on top of the defaults,
ignore globs `**/*.test.ts, **/legacy/**`, the image from the config, and
`--details 5` behaviour (from #325).

## 7. Docs and tests

#322 updates, in the same PR:

- `long_help` in `commands/python.json` (the config file and `--no-config`)
  and the executor module docstring;
- the `js_complexity` row of the "Configuration file" table and
  `docs/guides/code_check/js_complexity.md`;
- tests under `python/tests/code_check/js_complexity/`, covering every key's
  valid and invalid values (booleans as numbers, `NaN`, negative numbers,
  empty `image`, `ext`, `details` before #325), each precedence rule, list
  merging and deduplication, `--no-config` with a broken file, a missing
  file, a missing section, an empty section, `image` from the config
  avoiding the `VERSION` read, and a file with only `file_size`/`rubycritic`
  sections loading the defaults.

#325 adds the `details` key, its tests and its docs.
