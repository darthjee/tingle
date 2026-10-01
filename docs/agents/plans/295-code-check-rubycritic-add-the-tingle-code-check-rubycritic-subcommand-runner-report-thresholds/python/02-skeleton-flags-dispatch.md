# Package skeleton, flags, image and dispatch

Create `python/code_check/rubycritic/`, laid out like `file_size/`.

**`__init__.py`**: a docstring only.

**`constants.py`**: `class Constants` with `ClassVar`s:
- `DEFAULT_WARN = 100`, `DEFAULT_ERROR = 200`, `DEFAULT_CRITICAL = 400`
- `DEFAULT_EXCLUDES = [*FileSizeConstants.DEFAULT_EXCLUDES, "tmp", "log", ".bundle"]`
- `EXTENSIONS = [".rb"]`
- `IMAGE_REPO = "darthjee/tingle_rubycritic"`
- `VERSION_FILE = Path(__file__).resolve().parents[3] / "shell" / "linux" / "VERSION"`
- `DOCKER_INFO_TIMEOUT = 30`
- `NON_REEK_SMELL_TYPES = ("DuplicateCode", "HighComplexity", "VeryHighComplexity")`
- `MOUNT_ERROR_MARKERS = ("mounts denied", "not shared from the host")`

**`errors.py`**: `class RubycriticError(Exception)`, which carries the user-facing message.

**`flags.py`**: `FLAGS` in the same dict shape as `file_size.flags`.
- Flags: `path`, `--warn`/`--error`/`--critical` (`type=float`, `default=None`), `--top` (int), `--min-level` (choices `FileAnalyzer.LEVELS`), `--fail-on` (choices warn/error/critical) and `--image`.
- Take the help texts from spec §2.
- Import only `constants` and `file_size.file_analyzer`, so completion stays light.

**`image.py`**: `resolve_image(cli_image, version_file=Constants.VERSION_FILE) -> str`.
- If `--image` is given, return it.
- Otherwise read the version with `"".join(text.split())` and return `darthjee/tingle_rubycritic:<version>`.
- On `OSError` or an empty result, raise `RubycriticError` with the spec §10 message suggesting `--image`.

**`executor.py`, first part of `CheckRubycritic`:**
- `run(args)`: with no args, print help and exit 0.
- `_parse`: remap argparse exit 2 to 1, copied from `CheckFileSize._parse`.
- `_validate`: negative or NaN thresholds, a negative `--top` and an empty `--image` are usage errors (exit 1). It runs before path resolution.
- Apply the defaults: `SINGLE_DEFAULTS` after parsing.
- `_resolve_target`:
  - missing path → `path not found`;
  - `os.access` R_OK fails (plus X_OK for a directory) → `path not readable`;
  - a mount root (the directory, or the parent of a single file) that contains `:` → error.
- Then resolve the image.
- `_print_header`: `Analyzing:`, `Thresholds: warn=… | error=… | critical=…` (formatted with `format(v, "g")`) and `Image:`.
- Reuse `file_size.file_analyzer.FileAnalyzer` for levels and labels. It already handles floats.

**Registration:**
- Add `"rubycritic": (CheckRubycritic, "Ruby code complexity via RubyCritic (Docker).")` to `SUBCOMMANDS` in `python/code_check/executor.py`, after `file_size`, and add a usage line to that module's docstring.
- Set `SUBCOMMAND_NAMES = ("file_size", "rubycritic")` in `python/code_check/subcommands.py`.

Tests cover:
- help with no args;
- the usage-error remap;
- each validation error;
- path not found and not readable (mock `os.access`);
- `:` in the mount root;
- image resolution: explicit, from a `tmp_path` VERSION file, and missing or empty;
- the header text;
- dispatch from `CodeCheck`.

## Files to Change
- `python/code_check/rubycritic/__init__.py`: new.
- `python/code_check/rubycritic/constants.py`: new.
- `python/code_check/rubycritic/errors.py`: new.
- `python/code_check/rubycritic/flags.py`: new.
- `python/code_check/rubycritic/image.py`: new.
- `python/code_check/rubycritic/executor.py`: new (parse, validate, resolve, header).
- `python/code_check/executor.py`: register `rubycritic` in `SUBCOMMANDS` and the docstring.
- `python/code_check/subcommands.py`: add `"rubycritic"` to `SUBCOMMAND_NAMES`.
- `python/tests/code_check/rubycritic/__init__.py`: new.
- `python/tests/code_check/rubycritic/test_flags.py`: new.
- `python/tests/code_check/rubycritic/test_image.py`: new.
- `python/tests/code_check/rubycritic/test_executor.py`: new.
- `python/tests/code_check/test_executor.py`: add rubycritic dispatch and list cases.
