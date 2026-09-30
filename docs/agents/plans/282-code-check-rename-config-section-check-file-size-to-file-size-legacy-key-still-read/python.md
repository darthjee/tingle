# Python Plan: code_check: rename config section check_file_size to file_size (legacy key still read)

Main plan: [plan.md](plan.md)

## Shared contracts

- Produce `CONFIG_SECTION = "file_size"` and `LEGACY_CONFIG_SECTION = "check_file_size"`
  in `python/code_check/file_size/executor.py`.
- Implement the behaviour matrix, the exact warning line and the exact error
  line from [plan.md](plan.md#shared-contracts). The cli and guide agents
  document these strings word for word.

## Implementation Steps

### Step 1 — Generic `load_sections` helper
In `python/code_check/config.py`, add:

```python
def load_sections(names: Iterable[str], path: Path | None = None) -> dict[str, dict | None]:
```

It reads and parses the file once, with `_read_json`. It returns `{name: section or None}`
for every requested name. The result is all `None` when the file is missing,
and `None` for a missing section. It raises the same `ConfigError`s as today:
`top level must be an object`, and `'<name>' must be an object` for each
present section that is not a dict. Rewrite `load_section(name, path)` as
`return load_sections([name], path)[name]`, keeping its signature,
docstring and behaviour. Update the module docstring to mention both functions.

Add tests to `python/tests/code_check/test_config.py`:
- missing file → every name maps to `None`;
- a mix of present and missing sections;
- a non-object section raises, naming that section;
- the file is read once: monkeypatch `_read_json` (or `Path.read_text`) with
  a call counter.
The existing `load_section` tests stay as they are.

### Step 2 — Executor: rename the section and handle the legacy key
In `python/code_check/file_size/executor.py`:
- `CONFIG_SECTION = "file_size"`, and add
  `LEGACY_CONFIG_SECTION = "check_file_size"` with a comment saying it is
  deprecated and that removing it is tracked in #286.
- Import `load_sections` instead of `load_section`.
- `_load_config`: when `no_config` is set, return `({}, None)` as today.
  Otherwise, inside the existing `try`:
  1. `sections = load_sections([CONFIG_SECTION, LEGACY_CONFIG_SECTION], path)`.
  2. If both are not `None`, raise `ConfigError(path, "both 'file_size' and 'check_file_size' sections are set; keep only 'file_size'")`
     (build the message from the constants).
  3. If only the legacy section is present, call a new
     `_warn(message)` static method first. Like `_fail`, it prints
     `f"{err.YELLOW}Warning: {message}{err.RESET}"` to stderr with
     `Palette(sys.stderr)`, where message =
     `f"{path}: 'check_file_size' section is deprecated; rename it to 'file_size'."`.
     Then use the legacy section.
  4. If neither is present, return `({}, None)`. Otherwise return
     `(validate(section, path), path)`.
  Update the `_load_config` docstring.
- Module docstring: say the options are read from the `file_size` section,
  that the `check_file_size` section is still read with a deprecation warning,
  and that setting both is an error. Change the example config to `{"file_size": {...}}`.

In `python/code_check/file_size/config.py`, change the module docstring, the
`SCHEMA` comment and the `validate` docstring to say the `file_size` section.

Tests in `python/tests/code_check/file_size/test_executor_config.py`:
- change every existing `"check_file_size"` key to `"file_size"`, including
  the parametrised error cases. The expected reason becomes
  `"'file_size' must be an object"`;
- legacy only (`{"check_file_size": {"warn": 10}}`): `warn=10` is applied,
  stderr is exactly the warning line plus a newline (no ANSI codes under capsys),
  and the `Config: <path>` header is present;
- legacy only and invalid (`{"check_file_size": {"warn": -1}}`): exit 1,
  stdout is empty, stderr has the warning line followed by the `Error: <path>: ` line;
- both keys: exit 1, stdout is empty, stderr starts with
  `Error: <path>: both 'file_size' and 'check_file_size' sections are set`,
  and contains no `Warning:`;
- both keys with `--no-config`: runs normally, stderr is empty, and there is
  no `Config:` line;
- a `file_size` section next to an unrelated top-level key still loads with
  no warning.

## Files to Change
- `python/code_check/config.py` — add `load_sections`; `load_section` delegates to it.
- `python/code_check/file_size/executor.py` — the constants, `_warn`, `_load_config`, and the docstrings.
- `python/code_check/file_size/config.py` — comments and docstrings name the `file_size` section.
- `python/tests/code_check/test_config.py` — tests for `load_sections`.
- `python/tests/code_check/file_size/test_executor_config.py` — move the existing cases to `file_size`, and add the legacy, both-set and `--no-config` cases.

## CI Checks
- `python/`: `cd python && ruff check .` (CI job: `lint`)
- `python/`: `cd python && pytest` (CI job: `tests`)

## Notes
- The `python/check_file_size/` alias shim needs no change: it calls the
  same executor, so it gets the new behaviour automatically.
- Keep the generic `"check_file_size"` section names in
  `tests/code_check/test_config.py`. There they are just example section names.
- Manual check, with `HOME` set to a temp dir: a `file_size` section applies;
  a `check_file_size` section applies and warns; an invalid legacy section
  warns and then errors; both sections set exits 1.
