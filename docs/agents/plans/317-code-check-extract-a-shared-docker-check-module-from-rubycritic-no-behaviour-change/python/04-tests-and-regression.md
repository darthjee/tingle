# Add docker_check tests and verify rubycritic is unchanged

Add `python/tests/code_check/docker_check/` (with `__init__.py`), with one test file per module. `docker` is never run: mock `shutil.which` and `subprocess.run`.

- `test_docker_runner.py`:
  - both templated messages, with a non-default `command`/`tool`;
  - a custom `error_class` raised on each failure path (missing docker, `docker info` failure or timeout, pull failure, `OSError` on run, mount hint on status 125, generic failure);
  - `run_args`, the stdin encoding and `decode`/`write_stderr`.
- `test_image.py`:
  - `cli_image` wins;
  - another `repo` with a version file (whitespace stripped);
  - a missing, empty or unreadable file raises the given `error_class` with the exact message.
- `test_selection.py`:
  - another `extensions` list;
  - a `skip` predicate on a plain file and on a symlink (called on the walked path);
  - `skip=None` matches today's behaviour;
  - unsendable names;
  - `outside_symlinks` confinement.
- `test_executor.py`: drive `DockerCheck` with a minimal fake subclass (fake parser and reporter, hooks returning canned data). Cover:
  - no args prints help and exits 0;
  - an argparse error exits 1;
  - the config merge order and list dedup;
  - `--no-config`;
  - `_validate` with and without a `details` option;
  - `_resolve_target` errors (missing path, unreadable path, `:` in the root);
  - the header;
  - the "no files" message exits 0;
  - the `--fail-on` gate exits 2 through `_gate_value`;
  - `error_class` turned into `Error:` and exit 1.

Then run the existing `python/tests/code_check/rubycritic/` suite. The only allowed edits there are import-path changes (an `import` line or a `monkeypatch.setattr` target): no assertion changes and no deleted tests. Ideally the wrappers make no edit necessary. Run the full `pytest` (coverage at or above 75%) and `ruff check .`, and diff `--help` and the main error outputs before and after.

## Files to Change
- `python/tests/code_check/docker_check/__init__.py` — new package marker.
- `python/tests/code_check/docker_check/test_docker_runner.py` — new; covers the parameterised runner.
- `python/tests/code_check/docker_check/test_image.py` — new; covers `resolve_image` with another repository.
- `python/tests/code_check/docker_check/test_selection.py` — new; covers `extensions` and `skip`.
- `python/tests/code_check/docker_check/test_executor.py` — new; covers `DockerCheck` through a fake check.
- `python/tests/code_check/rubycritic/*.py` — import-path edits only, and only if needed.
