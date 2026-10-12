# Python Plan: code_check: extract a shared docker_check module from rubycritic (no behaviour change)

Main plan: [plan.md](plan.md)

## Shared contracts

Produce exactly the layout in [plan.md](plan.md#shared-contracts), following [docker-check.md](../../specs/code_check/js_complexity/docker-check.md), which is normative. Each name must match the spec. A name may differ only if every rule in the spec still holds.

## Steps

- [01 — Add the docker_check runtime modules](python/01-docker-check-runtime-modules.md)
- [02 — Add the DockerCheck executor base class](python/02-docker-check-executor-base.md)
- [03 — Rewire rubycritic onto docker_check](python/03-rewire-rubycritic.md)
- [04 — Add docker_check tests and verify rubycritic is unchanged](python/04-tests-and-regression.md)

## CI Checks
- `python/`: `ruff check .` (CI job: lint)
- `python/`: `pytest`, coverage must stay at or above 75% (CI job: `tests`; locally `make tests` or `cd python && pytest`)

## Notes
- **Patch points (spec section 2.6).** The existing tests monkeypatch `code_check.rubycritic.executor.select_files`, `executor.load_section`, `CheckRubycritic._execute`, `os.access`, `docker_runner.subprocess.run`, `docker_runner.shutil.which` and `Constants.VERSION_FILE` (on `code_check.rubycritic.constants.Constants`).
  - `subprocess`, `shutil` and `os` are module objects, so patching their attributes is global. It still works as long as `code_check.rubycritic.docker_runner` keeps `subprocess` and `shutil` reachable as attributes: import them in the wrapper.
  - `select_files` and `load_section` must be called by `CheckRubycritic` through **its own module globals**. The base class reaches them through overridable hooks (for example `_select_files(...)` and `_load_section(...)`), which `CheckRubycritic` implements by calling the names imported into `code_check/rubycritic/executor.py`. Do not satisfy `test_load_config_no_config_does_not_read_the_file` only by accident.
  - `Constants.VERSION_FILE` is read at call time by the rubycritic `resolve_image` wrapper. Never capture it at import time.
- **Byte-for-byte output.** Diff `tingle code_check rubycritic --help` and a few error paths (no docker, bad path, invalid config, `--fail-on`) before and after the change, using a dummy `--image` with docker absent, to confirm nothing changed.
- `_validate`'s `--details` check runs only when the check has a `details` option (for example `"details" in SINGLE_DEFAULTS`).
- Keep every module standard-library only, with the `# nosec` comments on `subprocess` calls and the `D212` docstring style.
