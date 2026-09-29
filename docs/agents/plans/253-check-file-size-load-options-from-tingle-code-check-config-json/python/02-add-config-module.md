# Add config.py loader and validator

Create `python/check_file_size/config.py`:

- `DEFAULT_PATH` helper: `Path.home() / ".tingle" / "code_check" / "config.json"`, computed at call time (not import time) so `HOME` changes in tests apply.
- `class ConfigError(Exception)` with `path` and `reason`; `str()` gives `"<path>: <reason>"`.
- `load_section(name: str, path: Path | None = None) -> dict | None` — generic, knows nothing about `check_file_size`:
  - file missing → `None`;
  - unreadable file / invalid JSON → `ConfigError`;
  - top level not a dict → `ConfigError("top level must be an object")`;
  - section missing → `None`; section not a dict → `ConfigError("'<name>' must be an object")`;
  - otherwise returns the section dict.
  Returning `None` (not `{}`) for "missing" lets the executor tell "no section" from "empty section" for the `Config:` header line. (The spec says `{}`; the `product-owner` updates it to match.)
- `SCHEMA: dict[str, Callable]` — key → validator, for the 12 keys in the shared contract. Small reusable validators: non-negative int (reject bool), list of str, bool, one-of choices (with optional `None`).
- `validate(section: dict, path: Path) -> dict` — raises `ConfigError(path, "unknown key '<k>'")` for keys not in `SCHEMA` and `ConfigError(path, "'<k>' must be ...")` for bad values; returns the section unchanged.

Docstrings follow the repo's pydocstyle rules (summary on the first line, D212).

## Files to Change
- `python/check_file_size/config.py` — new module: `ConfigError`, `load_section`, `SCHEMA`, `validate`.
