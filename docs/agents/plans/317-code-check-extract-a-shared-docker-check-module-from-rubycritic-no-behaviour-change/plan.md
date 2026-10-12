# Plan: code_check: extract a shared docker_check module from rubycritic (no behaviour change)

Issue: [317-code-check-extract-a-shared-docker-check-module-from-rubycritic-no-behaviour-change.md](../../issues/317-code-check-extract-a-shared-docker-check-module-from-rubycritic-no-behaviour-change.md)

Spec (normative): [docker-check.md](../../specs/code_check/js_complexity/docker-check.md)

## Overview
Move the tool-agnostic Docker plumbing of `python/code_check/rubycritic/` into a new package, `python/code_check/docker_check/`, and rebuild `rubycritic` on top of it, with byte-for-byte identical behaviour. Tool-specific values become parameters (`error_class`, `command`, `tool`, `repo`, `version_file`, `extensions`, `skip`) or class attributes and hooks on a `DockerCheck` base class. `rubycritic` keeps thin wrappers with today's signatures, so its existing tests only need import-path edits, if any. The architecture doc is then updated to describe the new package.

## Agents involved

- [python](python.md)
- [product-owner](product-owner.md)

## Shared contracts

The final layout and public names that the `product-owner` documents, and that the `python` agent produces:

- `python/code_check/docker_check/`:
  - `constants.py`: `Constants.DOCKER_INFO_TIMEOUT = 30`, `MOUNT_ERROR_MARKERS = ("mounts denied", "not shared from the host")`, `VERSION_FILE = <repo>/shell/linux/VERSION`.
  - `errors.py`: `DockerCheckError(message)`, with `.message`.
  - `docker_runner.py`: `DOCKER`, `decode`, `write_stderr` and `DockerRunner(image, *, error_class, command, tool)`, with `preflight`, `ensure_image`, `run`, `run_args` and `check_outcome`.
  - `image.py`: `resolve_image(cli_image, repo, version_file, *, error_class) -> str`.
  - `selection.py`: `Selection`, `unsendable_reason`, `build_selection` and `select_files(target, root, *, extensions, excludes, ignore=None, include=None, gitignore=True, skip=None)`.
  - `executor.py`: `DockerCheck`, the base class for `CheckRubycritic` (and later `CheckJsComplexity`).
- `python/code_check/rubycritic/` keeps:
  - `flags.py`, `constants.py` (every current attribute; the shared ones are assigned from `docker_check`), `config.py`, `output_parser.py` and `reporter.py`;
  - `errors.py`: `RubycriticError(DockerCheckError)`;
  - thin wrappers with today's signatures: `image.py` (`resolve_image(cli_image, version_file=None)`), `selection.py` (`select_files(target, root, *, excludes=None, ignore=None, include=None, gitignore=True)`, re-exporting `Selection`, `unsendable_reason` and `build_selection`) and `docker_runner.py` (a `DockerRunner(image)` subclass, re-exporting `decode` and `write_stderr`);
  - `executor.py`: `CheckRubycritic(DockerCheck)` with `_parse_output`, `_check_methods` and `_execute`.
- Display filtering (`--min-level`, `--top`) stays in each reporter.
- Nothing outside `python/` and `docs/agents/` changes (no image, CI, Makefile, `file_size` or user guide).
