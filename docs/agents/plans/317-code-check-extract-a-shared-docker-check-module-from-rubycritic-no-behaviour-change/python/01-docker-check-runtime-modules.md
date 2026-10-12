# Add the docker_check runtime modules

Create `python/code_check/docker_check/` with `__init__.py` and the modules below. Move the code from `rubycritic/`, unchanged except for the new parameters (spec sections 2.1 to 2.5).

- `constants.py`: a `Constants` class with `DOCKER_INFO_TIMEOUT = 30`, `MOUNT_ERROR_MARKERS = ("mounts denied", "not shared from the host")` and `VERSION_FILE = Path(__file__).resolve().parents[3] / "shell" / "linux" / "VERSION"` (same depth as `rubycritic`, so it still points to the repo root).
- `errors.py`: `DockerCheckError(Exception)`, with `__init__(message)` storing `.message`. This is today's `RubycriticError` body.
- `docker_runner.py`: `DOCKER`, `decode`, `write_stderr` and `DockerRunner(image, *, error_class, command, tool)`, with `preflight`, `ensure_image`, `run`, `run_args`, `check_outcome`, `_quiet_ok` and `_pull`.
  - Every `raise` uses `self.error_class`.
  - Only two messages are templated:
    - `docker not found on PATH; {command} needs Docker to run {tool}`;
    - `{tool} failed in {image} (exit {status})`.
  - Keep the line wrapping of the "docker not found" string so the rendered text is identical.
  - Every other message, `run_args` and the timeouts and markers (from `docker_check.constants`) stay as they are today.
- `image.py`: `resolve_image(cli_image, repo, version_file, *, error_class) -> str`. Same logic and same error message as today.
- `selection.py`: `Selection`, `unsendable_reason` and `build_selection` move unchanged. Add `select_files(target, root, *, extensions, excludes, ignore=None, include=None, gitignore=True, skip=None)`:
  - It builds `FileCollector(excludes, extensions, ignore=..., include=..., gitignore=..., binary_check=False, outside_symlinks=False)`.
  - It then drops each collected path for which `skip(path)` is true. `skip` is called on the walked path, before resolving it.
  - Finally it calls `build_selection`.

Write module docstrings in the existing style, made tool-neutral.

## Files to Change
- `python/code_check/docker_check/__init__.py` — new package marker.
- `python/code_check/docker_check/constants.py` — new; the shared constants.
- `python/code_check/docker_check/errors.py` — new; `DockerCheckError`.
- `python/code_check/docker_check/docker_runner.py` — new; the parameterised runner (code moved from `rubycritic/docker_runner.py`).
- `python/code_check/docker_check/image.py` — new; the parameterised `resolve_image`.
- `python/code_check/docker_check/selection.py` — new; the selection helpers plus `extensions` and `skip`.
