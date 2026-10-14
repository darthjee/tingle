# Fix the outdated js_complexity section in architecture.md
The `python/code_check/js_complexity/` paragraph in
`docs/agents/architecture.md` (around lines 227-240) still describes the
state before #321/#322: it says there is "no `config.py` yet" and that the
executor overrides `_parse`, `_load_config` and `_selection_options` to turn
off config and file-selection options. `config.py` exists now, and
`executor.py` only overrides `_selection_options`.

Read `python/code_check/js_complexity/` (`config.py`, `executor.py`,
`flags.py`, `selection.py`, ...) and rewrite the paragraph and its file list
to match the code as it is now. Keep the `docker_check` documentation as is.
It is already the permanent home of the `docker-check.md` contract. Check
that nothing normative from `specs/code_check/js_complexity/docker-check.md`
(package layout, what stays in `rubycritic/`, backward compatibility) is
missing, and add it if it is.

## Files to Change
- `docs/agents/architecture.md` — current `js_complexity` layout, `config.py` included, outdated "Until #321/#322" overrides removed.
