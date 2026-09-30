# Write config.md (#297)
Create `docs/agents/specs/code_check/rubycritic/config.md`, linking #297 at the top. Mirror `python/code_check/file_size/config.py` and `python/code_check/config.py`.

It must specify:
- **Section:** `rubycritic` in `~/.tingle/code_check/config.json`, loaded with `code_check.config.load_section("rubycritic")`. `SCHEMA`/`validate` live in `python/code_check/rubycritic/config.py`.
- **Keys and validators:**
  - `warn`/`error`/`critical`: a number ≥ 0, int or float, with booleans rejected
  - `top`: an int ≥ 0
  - `exclude`/`ignore`/`include`: a list of strings
  - `no_default_excludes`/`gitignore`: booleans
  - `fail_on`: `warn|error|critical|null`
  - `min_level`: `ok|warn|error|critical`
  - `image`: a non-empty string
  - There is no `ext` key.
- **Precedence:** CLI flags override single values, and list values are merged. Say the merge order.
- **Errors:** a missing file is fine; invalid JSON, an unknown key or a wrong type → the same error wording as `file_size`, exit 1. `--no-config` skips the file.
- **Example:** a full example config.

## Files to Change
- `docs/agents/specs/code_check/rubycritic/config.md`: new.
