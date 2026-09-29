# Tests

- `python/tests/check_file_size/test_config.py` (new), using explicit `path`s under `tmp_path` and the autouse `HOME` fixture:
  - `load_section`: missing file → `None`; missing section → `None`; other top-level keys ignored; empty section → `{}`; default path follows `HOME`; bad JSON, top level not an object, section not an object → `ConfigError` with path in the message.
  - `validate`: every key accepts a valid value; unknown key (incl. `path`) → error naming the key; each wrong type/value → error, including `"top": true`, negative ints, list with a non-str item, bad `fail_on`/`min_level`; `fail_on: null` accepted.
- `python/tests/check_file_size/test_executor.py` (extend), writing the config under `$HOME/.tingle/code_check/config.json`:
  - config single values apply (thresholds visible in the header, `top`, `min_level`, `fail_on` → exit 2);
  - CLI overrides config single values;
  - lists merged and deduplicated (`exclude`, `ignore`, `include`, `ext`) — spy on `FileCollector.__init__` like the existing tests;
  - `gitignore: false` and `no_default_excludes: true` apply; `--no-gitignore` wins over `gitignore: true`;
  - config error → red-free stderr message `Error: <path>: ...`, exit 1, empty stdout;
  - `--no-config` ignores a valid config and an invalid one;
  - `Config:` header line present only when a section was loaded (absent with no file, no section, or `--no-config`);
  - no-args help still exits 0 even with an invalid config.
- `_merge` unit tests (parametrized) for each key type.

## Files to Change
- `python/tests/check_file_size/test_config.py` — new.
- `python/tests/check_file_size/test_executor.py` — config integration and `_merge` tests.
