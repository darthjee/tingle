# Rewire rubycritic onto docker_check

Rebuild `python/code_check/rubycritic/` on top of `docker_check` (spec sections 2 and 3), with no behaviour change:

- `errors.py`: `class RubycriticError(DockerCheckError)`. The name stays, and the docstring keeps its meaning.
- `constants.py`: keep every attribute. Assign `VERSION_FILE`, `DOCKER_INFO_TIMEOUT` and `MOUNT_ERROR_MARKERS` from `docker_check.constants.Constants`. `VERSION_FILE` stays a class attribute that tests can patch.
- `image.py`: keep `resolve_image(cli_image, version_file=None)` as a wrapper. It calls `docker_check.image.resolve_image(cli_image, Constants.IMAGE_REPO, version_file or Constants.VERSION_FILE, error_class=RubycriticError)` and reads `Constants.VERSION_FILE` at call time.
- `selection.py`: re-export `Selection`, `unsendable_reason` and `build_selection`, and keep `select_files(target, root, *, excludes=None, ignore=None, include=None, gitignore=True)` as a wrapper. The wrapper binds `extensions=Constants.EXTENSIONS` and `excludes=Constants.DEFAULT_EXCLUDES if excludes is None else excludes`.
- `docker_runner.py`: a thin module.
  - `class DockerRunner(docker_check.docker_runner.DockerRunner)` with `__init__(image)`, which binds `error_class=RubycriticError`, `command="tingle code_check rubycritic"` and `tool="RubyCritic"`.
  - Re-export `decode`, `write_stderr` and `DOCKER`.
  - Keep `import shutil` and `import subprocess` so that `docker_runner.shutil` and `docker_runner.subprocess` stay reachable for the tests.
- `executor.py`: `CheckRubycritic(DockerCheck)` sets the class attributes and hooks from step 02:
  - `error_class = RubycriticError` and `validate_config = config.validate`;
  - `_load_section` and `_select_files` call this module's imported `load_section` and `select_files`;
  - `_gate_value` returns `complexity`.

  It keeps `_parse_output`, `_check_methods` and `_execute`, and keeps the module-level `PROG`, `CONFIG_SECTION`, `SINGLE_DEFAULTS`, `LIST_KEYS` and `THRESHOLD_KEYS` names. The module docstring (the `--help` source, if any) stays identical. Remove the moved code.

`python/code_check/subcommands.py` and the completion keep resolving `CheckRubycritic` and `FLAGS` as before. No change is expected there.

## Files to Change
- `python/code_check/rubycritic/errors.py` — subclass `DockerCheckError`.
- `python/code_check/rubycritic/constants.py` — assign the shared constants from `docker_check`.
- `python/code_check/rubycritic/image.py` — thin wrapper.
- `python/code_check/rubycritic/selection.py` — thin wrapper plus re-exports.
- `python/code_check/rubycritic/docker_runner.py` — thin `DockerRunner(image)` subclass plus re-exports.
- `python/code_check/rubycritic/executor.py` — `CheckRubycritic(DockerCheck)`, keeping only the RubyCritic-specific parts.
