# Spec: the shared `docker_check` package

Sub-issue: #317. Parent: #315. Shared contracts: [README.md](README.md).

#317 moves the tool-agnostic plumbing of `python/code_check/rubycritic/` into
a new package, `python/code_check/docker_check/`, and moves `rubycritic`
onto it **with no change in behaviour**. `js_complexity` (#320) is then built
on the same package. #317 is Python-only: no image, CI, Makefile or
`file_size` change.

## 1. Package layout

```
python/code_check/docker_check/
  __init__.py
  constants.py      DOCKER_INFO_TIMEOUT, MOUNT_ERROR_MARKERS, VERSION_FILE
  errors.py         DockerCheckError
  docker_runner.py  DockerRunner, decode, write_stderr
  image.py          resolve_image
  selection.py      Selection, unsendable_reason, build_selection, select_files
  executor.py       DockerCheck (base class for the executors)
```

Every module stays standard-library only, like the code it comes from. The
names below are taken from the current code; a name may be adjusted in #317
only if every rule in this spec still holds.

## 2. What moves, and its new parameters

### 2.1 Errors (`errors.py`)

- `DockerCheckError(Exception)`: the body of today's `RubycriticError`
  (`__init__(message)`, stores `.message`).
- `rubycritic/errors.py` keeps `RubycriticError`, now defined as
  `class RubycriticError(DockerCheckError)`, with the same name, module and
  docstring meaning. `js_complexity` adds `JsComplexityError(DockerCheckError)`.
- Every shared function or class that raises takes the **error class** to
  raise (`error_class: type[DockerCheckError]`), so `rubycritic` still raises
  `RubycriticError` everywhere it does today.

### 2.2 Constants (`constants.py`)

| Name | Value | From |
|------|-------|------|
| `DOCKER_INFO_TIMEOUT` | `30` | `rubycritic.constants.Constants` |
| `MOUNT_ERROR_MARKERS` | `("mounts denied", "not shared from the host")` | same |
| `VERSION_FILE` | `Path(__file__).resolve().parents[3] / "shell" / "linux" / "VERSION"` | same (the package sits at the same depth, so `parents[3]` is still the repo root) |

`rubycritic.constants.Constants` keeps every attribute it has today
(`DOCKER_INFO_TIMEOUT`, `MOUNT_ERROR_MARKERS` and `VERSION_FILE` included);
it may assign them from `docker_check.constants`.

### 2.3 Docker runner (`docker_runner.py`)

Moves: `DOCKER`, `decode`, `write_stderr` and `DockerRunner` with
`preflight`, `ensure_image`, `run`, `run_args`, `check_outcome`, `_quiet_ok`
and `_pull`, unchanged except for the parameters below.

```python
DockerRunner(image: str, *, error_class: type[DockerCheckError], command: str, tool: str)
```

| Parameter | `rubycritic` passes | `js_complexity` passes | Used in |
|-----------|---------------------|------------------------|---------|
| `image` | the resolved image | the resolved image | every Docker call |
| `error_class` | `RubycriticError` | `JsComplexityError` | every raise |
| `command` | `"tingle code_check rubycritic"` | `"tingle code_check js_complexity"` | `docker not found on PATH; {command} needs Docker to run {tool}` |
| `tool` | `"RubyCritic"` | `"FTA"` | the message above and `{tool} failed in {image} (exit {status})` |

- The run line (`run_args`) is unchanged and shared:
  `docker run --rm -i --pull never --network none --security-opt no-new-privileges --user <uid>:<gid> -v <root>:/src:ro -w /src <image>`.
- The other messages (`the Docker daemon is not responding ...`,
  `Pulling <image> ...`, `could not pull image <image>`,
  `could not run docker: <exc>`, the mount hint) have no tool-specific part
  and are shared as they are today.
- `rubycritic` builds its runner so that every message is byte-for-byte the
  current text. `rubycritic/docker_runner.py` may stay as a thin module that
  binds these parameters (for example a `DockerRunner` subclass whose
  `__init__(image)` keeps today's signature), or it may be removed with the
  tests' imports moved to `code_check.docker_check.docker_runner`.

### 2.4 Image resolution (`image.py`)

```python
resolve_image(cli_image: str | None, repo: str, version_file: Path, *, error_class: type[DockerCheckError]) -> str
```

- Same logic as today: `cli_image` wins when truthy; otherwise
  `f"{repo}:{version}"`, where `version` is `version_file`'s content with all
  whitespace removed. A missing, unreadable or empty file raises
  `error_class("cannot read the tingle version from <file>; use --image to choose the image")`.
- The caller passes `version_file` **at call time** from its own
  `Constants.VERSION_FILE`, so a test that patches
  `rubycritic.constants.Constants.VERSION_FILE` keeps working.
- `rubycritic/image.py` keeps `resolve_image(cli_image, version_file=None)`
  with today's signature, as a wrapper that passes
  `Constants.IMAGE_REPO` (`darthjee/tingle_rubycritic`),
  `version_file or Constants.VERSION_FILE` and `RubycriticError`.
  `js_complexity` passes `darthjee/tingle_js_complexity` and
  `JsComplexityError`.

### 2.5 Selection (`selection.py`)

Moves: `Selection`, `unsendable_reason` and `build_selection`, unchanged.
`select_files` gains the check-specific parameters:

```python
select_files(
    target: Path,
    root: Path,
    *,
    extensions: list[str],
    excludes: list[str],
    ignore: list[str] | None = None,
    include: list[str] | None = None,
    gitignore: bool = True,
    skip: Callable[[Path], bool] | None = None,
) -> Selection
```

| Parameter | `rubycritic` | `js_complexity` |
|-----------|--------------|-----------------|
| `extensions` | `[".rb"]` | the core list (and, from #326, the SFC list) from [README.md](README.md#4-extensions) |
| `excludes` | `Constants.DEFAULT_EXCLUDES` merged with `--exclude` (today's default when `None`) | its own `DEFAULT_EXCLUDES` merged with `--exclude` |
| `skip` | `None` | the declaration-file rule, plus the minified rule unless `no_default_excludes` (see [file-selection.md](file-selection.md#2-extensions-and-skip-rules)) |

- It builds `file_size`'s `FileCollector(excludes, extensions, ignore=...,
  include=..., gitignore=..., binary_check=False, outside_symlinks=False)`
  exactly as `rubycritic` does today.
- `skip`, when given, is called on each path returned by
  `FileCollector.collect` (the walked path, before resolving a symlink); a
  path for which it returns `True` is dropped silently, before
  `build_selection`. With `skip=None` the result is today's.
- `rubycritic/selection.py` keeps `select_files(target, root, *, excludes=None,
  ignore=None, include=None, gitignore=True)` with today's signature, as a
  wrapper that binds `extensions=Constants.EXTENSIONS` and the default
  excludes. The rubycritic executor keeps calling it through its own module
  globals, so `monkeypatch.setattr(executor, "select_files", ...)` in the
  existing tests still intercepts it and sees the same keyword arguments.

### 2.6 Executor scaffolding (`executor.py`)

A base class, `DockerCheck`, holds the flow shared by every Docker-backed
check. `CheckRubycritic` and `CheckJsComplexity` subclass it. It moves these
`CheckRubycritic` members, unchanged except where a check-specific value is
read from a class attribute or hook:

| Member | Check-specific input |
|--------|----------------------|
| `_parse` (argparse exit 2 → 1) | none |
| `_fail`, `_warn` | none |
| `_load_config` | `CONFIG_SECTION`, `validate` (the check's config validator) |
| `_merge` | `SINGLE_DEFAULTS`, `LIST_KEYS` |
| `_validate` | `THRESHOLD_KEYS`, `error_class`; the `--details` check runs only when the check has a `details` option |
| `_resolve_target` | `error_class` |
| `_print_header` (`Analyzing:`, `Thresholds:`, `Image:`, `Config:`) | `THRESHOLD_KEYS` |
| `_selection_options` | `Constants.DEFAULT_EXCLUDES` of the check |
| `_select` | the check's `select_files`, the "no files" message (`No Ruby files found for analysis.` / `No JavaScript/TypeScript files found for analysis.`) |
| the `--fail-on` gate (`_gate_failed`) | the value each result is classified by (rubycritic: `complexity`; js_complexity: the rounded `fta_score`) |
| `run(args)` (no args → help, exit 0; parse; load config; merge; validate; execute; `RubycriticError` → `Error:` + exit 1; non-zero status → `sys.exit`) | `FLAGS`, `PROG`, `error_class`, `_execute` |

**Display filtering** (`--min-level` then `--top`, `No files at or above
<LEVEL>.`) stays in each reporter: the column layout and the row type differ,
so only the rule is shared (see [subcommand.md](subcommand.md#6-report)).

The base class must not read any module global of
`code_check.rubycritic.executor` itself. Every patch point the existing
tests use (`executor.select_files`, `executor.load_section`,
`CheckRubycritic._execute`, `os.access`, `docker_runner.subprocess`,
`docker_runner.shutil`, `Constants.VERSION_FILE`) must still be reachable
from the test with, at most, an import-path edit.

## 3. What stays in `rubycritic/`

- `flags.py` (`FLAGS`), `constants.py` (thresholds, `DEFAULT_DETAILS`,
  `DEFAULT_EXCLUDES`, `EXTENSIONS`, `IMAGE_REPO`, `NON_REEK_SMELL_TYPES`, plus
  the attributes kept from section 2.2).
- `config.py` (`SCHEMA`, `validate`).
- `errors.py` (`RubycriticError`, now a `DockerCheckError` subclass).
- `output_parser.py` (the RubyCritic JSON contract) and `reporter.py`
  (columns, method lines, the `Score:` summary).
- `executor.py`: `CheckRubycritic` with `PROG`, `CONFIG_SECTION`,
  `SINGLE_DEFAULTS`, `LIST_KEYS`, `THRESHOLD_KEYS`, `_parse_output` (with its
  `could not parse the RubyCritic output from <image>: <reason>` message),
  `_check_methods` and `_execute`.
- Thin wrappers, where section 2 asks for them (`select_files`,
  `resolve_image`, and optionally `DockerRunner`).

`code_check/excludes.py` (`parse_excludes`, `resolve_excludes`) and
`code_check/validators.py` are already shared; they do not move.

## 4. Backward compatibility (normative)

These invariants hold after #317, and after every later sub-issue of #315.

### 4.1 `rubycritic` is unchanged

- For every input, `tingle code_check rubycritic` produces **byte-for-byte
  identical** stdout, stderr and exit codes, the same `--help`, the same
  tab completion and the same config validation as before #317.
- The existing tests under `python/tests/code_check/rubycritic/` keep
  passing. **Only import-path edits are allowed** in them: a changed
  `import` line or a changed `monkeypatch.setattr` target that names the new
  module. No assertion changes and no deleted tests.
- Error class names (`RubycriticError`), message wording and the
  `rubycritic` config section stay as they are. A shared message wording
  that would change `rubycritic`'s output is not allowed: tool-specific parts
  are parameters (section 2.3), and the unparsable-output message stays in
  `rubycritic`'s executor.

### 4.2 The `rubycritic` image is untouched

`darthjee/tingle_rubycritic`, `docker/rubycritic/` and its stdin/stdout
contract do not change. #317 changes nothing outside `python/` and its docs.

### 4.3 `file_size` is untouched

`FileCollector`, `code_check.excludes` and `file_size`'s behaviour stay as
they are. `docker_check` only wraps them. Any new parameter added to a
shared helper is optional, with today's behaviour as its default.

## 5. Tests

- New tests go under `python/tests/code_check/docker_check/`, one file per
  module (`test_docker_runner.py`, `test_image.py`, `test_selection.py`,
  `test_executor.py`), with `docker` never run (`shutil.which` and
  `subprocess.run` mocked).
- They cover the parameters: the two message templates for a non-default
  `command`/`tool`, `error_class` being raised, `resolve_image` with another
  repository, `select_files` with another extension list and with a `skip`
  predicate (on a plain file and on a symlink), and the base class driven by
  a minimal fake check.
- The existing `python/tests/code_check/rubycritic/` tests stay as described
  in section 4.1. Coverage stays at or above 75%.

## 6. Docs

#317 updates `docs/agents/architecture.md` with the `docker_check` package
and what each check keeps. User guides do not change.
