# Extract shared helpers and FLAGS
Promote the helpers that now have a second consumer, following the issue's rule: a helper moves up only once a second
consumer needs it.

- **Palette:** `git mv python/code_check/file_size/palette.py python/code_check/palette.py`. Move the raw ANSI codes
  (`RESET`, `BOLD`, `DIM`, `GREEN`, `YELLOW`, `RED`, `MAGENTA`, `CYAN`, `GRAY`, currently in `constants.py` L11-23) into
  a `Colors` class in `code_check/palette.py`. `Palette` then reads `getattr(Colors, name)` and no longer imports any
  `file_size` module. `file_size/constants.py` keeps only the thresholds, `DEFAULT_EXCLUDES` and
  `BINARY_EXTENSIONS`. Update `reporter.py` (`from .palette` → `from code_check.palette import Palette`) and the
  executor import. Move `test_palette.py` to `python/tests/code_check/test_palette.py`, and point it and
  `test_reporter.py` (L8, L141-142) at `code_check.palette.Colors`.
- **Generic config:** create `python/code_check/config.py` holding `default_path()`, `ConfigError`, `_MISSING`,
  `_read_json` and `load_section(name, path)`. These are needed together, because `load_section` raises `ConfigError`.
  `file_size/config.py` keeps `SCHEMA`/`validate` and imports `ConfigError` from `code_check.config`. It may re-export
  it so `executor.py` keeps a single import site. The section name stays `check_file_size`. Split `test_config.py`:
  the generic `default_path`/`load_section` cases go to `python/tests/code_check/test_config.py`, and the
  SCHEMA/validate cases stay in `tests/code_check/file_size/test_config.py`.
- **FLAGS:** move `FLAGS` (executor.py L63-~160) to a new `python/code_check/file_size/flags.py`, which imports only
  `constants` and `file_analyzer` (for `LEVELS`). `executor.py` imports `FLAGS` from there. Completion (step 05) will
  import only this module.

## Files to Change
- `python/code_check/palette.py` — moved from `file_size/`, now with the `Colors` class.
- `python/code_check/file_size/constants.py` — remove the ANSI codes.
- `python/code_check/file_size/reporter.py`, `executor.py` — update imports.
- `python/code_check/config.py` — new, generic loader plus `ConfigError`.
- `python/code_check/file_size/config.py` — keep only `SCHEMA`/`validate`, and import `ConfigError`.
- `python/code_check/file_size/flags.py` — new, holds `FLAGS`.
- `python/tests/code_check/test_palette.py`, `test_config.py` — moved or split tests.
- `python/tests/code_check/file_size/test_reporter.py`, `test_config.py` — updated imports and the remaining cases.
