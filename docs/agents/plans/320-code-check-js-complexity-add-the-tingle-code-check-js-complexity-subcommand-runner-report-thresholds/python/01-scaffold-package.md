# Scaffold the package (constants, errors, flags, wrappers, selection)
Create `python/code_check/js_complexity/` with the import-light and thin-wrapper modules, mirroring `rubycritic/` (spec §1, file-selection §2/§3/§5/§7):

- `__init__.py`: a one-line module docstring.
- `constants.py`: `Constants` with:
  - `DEFAULT_WARN = 50`, `DEFAULT_ERROR = 60`, `DEFAULT_CRITICAL = 75`;
  - `DEFAULT_EXCLUDES = [*FileSizeConstants.DEFAULT_EXCLUDES, ".turbo", ".svelte-kit", ".output", ".vercel", ".parcel-cache", "storybook-static"]`;
  - `EXTENSIONS` (the 8 core extensions);
  - `DECLARATION_SUFFIXES = (".d.ts", ".d.mts", ".d.cts")`;
  - `IMAGE_REPO = "darthjee/tingle_js_complexity"`;
  - `VERSION_FILE`, taken from `docker_check`.
- `errors.py`: `JsComplexityError(DockerCheckError)`.
- `flags.py`: `FLAGS` for `path`, `--warn/--error/--critical` (float), `--top` (int), `--min-level` (choices `ok|warn|error|critical`), `--fail-on` (choices `warn|error|critical`) and `--image`. Use the spec §2 help texts. Single values default to `None`. The module depends only on `constants` (import-light, read by completion).
- `image.py`: `resolve_image(cli_image, version_file=None)`, binding `IMAGE_REPO`, `VERSION_FILE` and `JsComplexityError` onto `docker_check.image.resolve_image`.
- `docker_runner.py`: a `DockerRunner(image)` subclass binding `error_class=JsComplexityError`, `command="tingle code_check js_complexity"` and `tool="FTA"`. Re-export `decode` and `write_stderr`, and keep `shutil`/`subprocess` reachable for the tests, as `rubycritic/docker_runner.py` does.
- `selection.py`: `select_files(target, root, *, excludes=None, ignore=None, include=None, gitignore=False)` calling `docker_check.selection.select_files` with:
  - `extensions=Constants.EXTENSIONS`;
  - the default excludes;
  - a `skip` predicate dropping names whose `path.name.lower()` ends with a declaration suffix.
  
  Re-export `Selection`, `build_selection` and `unsendable_reason`. Check that `FileCollector` matches extensions on `path.suffix.lower()`, so `UPPER.JS` is kept and `.d.ts` reaches the skip predicate as `.ts`.

Tests (`python/tests/code_check/js_complexity/`, new `__init__.py`):
- `test_flags.py`: names, types, choices and `None` defaults;
- `test_image.py`: `--image` wins, version tag, whitespace stripped, missing or empty version file;
- `test_docker_runner.py`: the bound messages (`... needs Docker to run FTA`, `FTA failed in <image> (exit N)`, mount hint);
- `test_selection.py`: each extension in mixed case, `.d.ts/.d.mts/.d.cts` skipped (directory and single file), the default excludes (including the 6 new ones), an outside or dangling symlink skipped, newline and non-UTF-8 names warned, a non-UTF-8 file content still selected, a single file with an unsupported extension giving nothing.

## Files to Change
- `python/code_check/js_complexity/__init__.py`: new.
- `python/code_check/js_complexity/constants.py`: new.
- `python/code_check/js_complexity/errors.py`: new.
- `python/code_check/js_complexity/flags.py`: new.
- `python/code_check/js_complexity/image.py`: new.
- `python/code_check/js_complexity/docker_runner.py`: new.
- `python/code_check/js_complexity/selection.py`: new.
- `python/tests/code_check/js_complexity/__init__.py`, `test_flags.py`, `test_image.py`, `test_docker_runner.py`, `test_selection.py`: new.
