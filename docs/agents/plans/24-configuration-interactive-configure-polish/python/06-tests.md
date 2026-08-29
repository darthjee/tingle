# Tests

Cover the new behavior added in Steps 1–5, following the existing per-module test file convention (`python/tests/kube/test_<module>.py`, one file per `kube/` module).

- `test_config.py` (extend) — `raw` reflects the unmodified file contents (no defaults baked in); `validate()` rejects the same malformed shapes `_load` already rejects; `save()` writes valid drafts to disk and refuses (leaving the existing file untouched) on an invalid draft; a fresh path with no existing file is created (parent dirs included) on first `save()`.
- `test_configure.py` (new) — for each of `configure_context`/`configure_namespace`/`configure_pod`, drive the flow with mocked `input()` sequences (`monkeypatch` on `builtins.input`) covering: create, edit, remove, and an invalid entry that gets reprompted. Specifically assert:
  - Removing a context alias cascades to drop its `namespaces`/`pods` blocks.
  - `configure_pod`'s `id_pattern` prompt rejects an unparsable regex and reprompts.
  - Optional fields left blank are omitted from the saved dict rather than stored as empty strings.
- `test_executor.py` (extend) — `_configure` dispatches to the right `configure_*` function per `configure_target`; `--json` on `list namespace`/`list pods` produces valid JSON matching the documented shape (Step 4); `_list_pods` prints discarded candidates when an alias matches nothing (Step 5).
- `test_parser.py` (extend) — `--json` parses correctly on both `list namespace` and `list pods`.

## Files to Change

- `python/tests/kube/test_config.py` — extend per above.
- `python/tests/kube/test_configure.py` — new.
- `python/tests/kube/test_executor.py` — extend per above.
- `python/tests/kube/test_parser.py` — extend per above.

## CI Checks

- `python`: `ruff check .` (CI job: `lint`)
- `python`: `pytest` (CI job: `tests`)
