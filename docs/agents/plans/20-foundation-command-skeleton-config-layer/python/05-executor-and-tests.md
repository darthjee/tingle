# Wire the executor and add unit tests

Flesh out `Kube.run(args)` (in `executor.py`, scaffolded in Step 1) to: parse `args` via the parser from Step 2, load the config via `KubeConfig` from Step 4 (printing the pass-through notice when applicable), and dispatch to a stub handler per subcommand (`switch`, `list`, `shell`, `configure`) that does nothing beyond confirming it was reached (e.g. prints "not yet implemented" or similar) — real behavior for each starts in child issues #21-#24. This is the orchestration glue; it must not duplicate parsing or config-validation logic already built in Steps 2-4.

Add unit tests covering the config layer end-to-end (schema validation, defaults applied correctly, pass-through triggered on missing file / invalid JSON / structurally invalid config) and a smoke test that the parser correctly identifies each subcommand and its arguments. Follow `python/tests/check_file_size/`'s structure and style (one test file roughly per source file, using the same test runner/fixtures conventions already in use there).

## Files to Change
- `python/kube/executor.py` — flesh out `Kube.run(args)` to wire parser + config + stub subcommand handlers.
- `python/tests/kube/__init__.py` — new, empty (package marker, matching `python/tests/check_file_size/__init__.py`).
- `python/tests/kube/test_config.py` — new. Covers `KubeConfig`: defaults applied, valid config parsed correctly, pass-through on missing/invalid file.
- `python/tests/kube/test_parser.py` — new. Covers the subcommand parser: each subcommand and its arguments are parsed into the expected shape.
