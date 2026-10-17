# Package skeleton and bindings
Create `python/code_check/php_complexity/` with the import-light and binding modules, laid out like `js_complexity/` (cli.md §1):

- `constants.py`: the `Constants` class exactly as in cli.md §1 (`DEFAULT_WARN/ERROR/CRITICAL`, `DEFAULT_EXCLUDES`, `EXTENSIONS`, `BLADE_SUFFIX`, `BOOTSTRAP_CACHE`, `IMAGE_REPO`, `VERSION_FILE`). Leave `DEFAULT_DETAILS` out until #351.
- `errors.py`: `PhpComplexityError(DockerCheckError)`.
- `docker_runner.py`: `DockerRunner` binding `error_class`, `COMMAND = "tingle code_check php_complexity"` and `TOOL = "PDepend"`. Re-export `DOCKER`, `decode` and `write_stderr`, and keep `shutil` and `subprocess` importable for patching.
- `image.py`: `resolve_image(cli_image, version_file=None)`.
- `flags.py`: `FLAGS` for the flags in cli.md §2, with help texts copied verbatim. It must stay import-light, because completion imports it.
- `selection.py`: `select_files` on top of `docker_check.selection.select_files`. It uses the `.php` extension, the default excludes, `binary_check=False`, and a `skip` predicate for `*.blade.php` (case-insensitive) and the `bootstrap/cache` segment pair (`skip_bootstrap_cache`, selection.md §4). A single-file `<path>` follows cli.md §8.8.
- `config.py`: a stub `SCHEMA`/`validate` that accepts nothing.

Add the unit tests: `test_flags.py`, `test_image.py`, `test_docker_runner.py` (preflight, pull, mount-denied and non-zero exits) and `test_selection.py` (`.php` in any case, Blade skipped in a directory and as a single file, default excludes, `bootstrap/cache`, unsendable names, symlinks).

## Files to Change
- `python/code_check/php_complexity/__init__.py` — new package
- `python/code_check/php_complexity/constants.py` — new
- `python/code_check/php_complexity/errors.py` — new
- `python/code_check/php_complexity/docker_runner.py` — new
- `python/code_check/php_complexity/image.py` — new
- `python/code_check/php_complexity/flags.py` — new
- `python/code_check/php_complexity/selection.py` — new
- `python/code_check/php_complexity/config.py` — new stub
- `python/tests/code_check/php_complexity/__init__.py`, `test_flags.py`, `test_image.py`, `test_docker_runner.py`, `test_selection.py` — new tests
