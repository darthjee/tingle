# Issue: code_check: extract a shared docker_check module from rubycritic (no behaviour change)

## Description
Extract the tool-agnostic Docker plumbing of `tingle code_check rubycritic` into a shared package, `python/code_check/docker_check/`, and move `rubycritic` onto it **with no change in behaviour**. This prepares the ground for `tingle code_check js_complexity` (parent #315), which reuses the same plumbing instead of copying it.

The spec [`docs/agents/specs/code_check/js_complexity/docker-check.md`](../specs/code_check/js_complexity/docker-check.md) is **normative** and wins over this issue wherever they differ (see the specs [README](../specs/code_check/js_complexity/README.md)).

## Problem
`python/code_check/rubycritic/` mixes Ruby-specific code (the RubyCritic JSON parser, reporter columns, config schema) with plumbing that any Docker-backed check needs:
- the `docker` preflight;
- image pull and resolution;
- the sandboxed `docker run` with the file list on stdin;
- outcome checks with the Docker Desktop hint;
- stdin-safe file selection;
- config loading and merging, target resolution, the header, the `--fail-on` gate and the `run` flow.

A second Docker-backed check would otherwise have to copy about 400 lines, or import from `code_check.rubycritic`.

## Expected Behavior
- A new `python/code_check/docker_check/` package (standard library only) holds:
  - `constants.py`: `DOCKER_INFO_TIMEOUT`, `MOUNT_ERROR_MARKERS`, `VERSION_FILE`.
  - `errors.py`: `DockerCheckError` (the body of today's `RubycriticError`). `RubycriticError` becomes a subclass of it.
  - `docker_runner.py`: `DockerRunner(image, *, error_class, command, tool)`, `decode` and `write_stderr`, which cover:
    - the preflight (`docker info`);
    - `ensure_image` and the pull, with `Pulling <image> ...` on stderr;
    - `run`, with an unchanged `run_args` (`docker run --rm -i --pull never --network none --security-opt no-new-privileges --user <uid>:<gid> -v <root>:/src:ro -w /src <image>`) and the file list on stdin;
    - `check_outcome`, including the Docker Desktop file-sharing hint.

    `command` and `tool` fill only the two tool-specific messages (`docker not found on PATH; {command} needs Docker to run {tool}` and `{tool} failed in {image} (exit {status})`).
  - `image.py`: `resolve_image(cli_image, repo, version_file, *, error_class)`. The caller passes `version_file` at call time.
  - `selection.py`: `Selection`, `unsendable_reason` and `build_selection`, unchanged, plus `select_files(target, root, *, extensions, excludes, ignore, include, gitignore, skip=None)`. It is built on `file_size`'s `FileCollector`. `skip` drops a walked path silently, and `skip=None` gives today's result.
  - `executor.py`: a `DockerCheck` base class. It holds `_parse`, `_fail`, `_warn`, `_load_config`, `_merge`, `_validate`, `_resolve_target`, `_print_header`, `_selection_options`, `_select`, `_gate_failed` and `run`. Check-specific values come from class attributes or hooks (`CONFIG_SECTION`, `SINGLE_DEFAULTS`, `LIST_KEYS`, `THRESHOLD_KEYS`, `FLAGS`, `PROG`, `error_class`, the validator, `select_files`, the "no files" message and the gate value).
- **Display filtering** (`--min-level`, then `--top`) stays in each reporter. Only the rule is shared.
- `python/code_check/rubycritic/` keeps only its own parts:
  - `flags.py`, `constants.py` (every current attribute, the shared ones assigned from `docker_check.constants`), `config.py`, `errors.py`, `output_parser.py` and `reporter.py`;
  - `executor.py`, with `CheckRubycritic(DockerCheck)` keeping `_parse_output`, `_check_methods` and `_execute`;
  - thin wrappers that keep today's signatures: `select_files` in `selection.py`, `resolve_image` in `image.py` and `DockerRunner(image)` in `docker_runner.py`.
- **No change in behaviour:**
  - `tingle code_check rubycritic` gives byte-for-byte identical stdout, stderr, exit codes, `--help`, tab completion and config validation;
  - the existing tests under `python/tests/code_check/rubycritic/` pass with **only import-path edits** (an `import` line or a `monkeypatch.setattr` target). No assertion is changed and no test is deleted;
  - every patch point those tests use (`executor.select_files`, `executor.load_section`, `CheckRubycritic._execute`, `os.access`, `docker_runner.subprocess`, `docker_runner.shutil`, `Constants.VERSION_FILE`) stays reachable;
  - the `DockerCheck` base class reads no module global of `code_check.rubycritic.executor`.
- New tests in `python/tests/code_check/docker_check/` (`test_docker_runner.py`, `test_image.py`, `test_selection.py`, `test_executor.py`) never run `docker`. They cover:
  - non-default `command`/`tool` messages;
  - the `error_class` that is raised;
  - another image repository;
  - another extension list;
  - a `skip` predicate, on a plain file and on a symlink;
  - the base class driven by a minimal fake check.

  Coverage stays at or above 75%.

## Solution
1. Create `docker_check/` and move the code, adding the parameters described in the spec (`error_class`, `command`, `tool`, `repo`, `version_file`, `extensions`, `skip`).
2. Rewire `rubycritic` onto it: make `RubycriticError` subclass `DockerCheckError`, make `CheckRubycritic` subclass `DockerCheck`, and turn `selection.py`, `image.py` and `docker_runner.py` into thin wrappers that keep today's signatures.
3. Add the new `docker_check` tests, and keep the rubycritic tests as regression coverage (import-path edits only).
4. Update `docs/agents/architecture.md` (and `folder-structure.md` if needed) to describe `docker_check` as the base for Docker-backed checks.

### Out of scope
- Anything specific to `js_complexity`.
- Changes to `file_size`, `code_check/excludes.py` or `code_check/validators.py`.
- Changes to the rubycritic image (`docker/rubycritic/`), CI or the Makefile.
- User guides.

### Agents
- `python`: the refactor and its tests.
- `product-owner`: the `docs/agents/architecture.md` update.

## Benefits
- `js_complexity`, and any later Docker-backed check, only needs a parser, a reporter, a schema, flags and an image.
- Fixes to Docker handling are made in one place.
