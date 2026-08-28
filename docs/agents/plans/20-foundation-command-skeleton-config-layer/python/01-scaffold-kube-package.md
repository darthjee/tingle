# Scaffold the kube package and dispatcher entrypoint

Create the `python/kube/` package, sibling to `python/check_file_size/`, following the repo's documented command-breakdown pattern (see `docs/agents/architecture.md`'s "Breaking a command down once it outgrows a single file"). `main.py` is a thin flow-verb dispatcher — it must not contain any subcommand logic itself, mirroring `python/check_file_size/main.py` exactly: read `argv[1]` as the flow verb, and for `run`, instantiate the orchestrator class and forward `argv[2:]` to it. `executor.py` holds the orchestrator class (name it `Kube`), which at this step can be a minimal shell — its `run(args)` method just needs to exist so `main.py` has something to call; full subcommand dispatch is wired in Step 5 once the parser (Step 2) and config loader (Step 4) exist.

## Files to Change
- `python/kube/__init__.py` — new, empty (package marker, matching `python/check_file_size/__init__.py`).
- `python/kube/main.py` — new. `run`/`complete` flow-verb dispatcher; for `run`, instantiate `Kube` (from `executor.py`) and call `.run(argv[2:])`. No `complete` handling needed yet (kube has no `completion.py` in this issue — the completion hub's generic file/folder fallback applies, same as `check_file_size` today).
- `python/kube/executor.py` — new. Minimal `Kube` class with a `run(args)` method (fleshed out fully in Step 5).
