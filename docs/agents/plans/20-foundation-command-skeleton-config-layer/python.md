# python Plan: Foundation: command skeleton + config layer

Main plan: [plan.md](plan.md)

## Shared contracts

- `python/kube/main.py` is the file `cli` points `commands/python.json`'s `"kube"` entry's `path` at. It must accept `run` as `argv[1]` (the flow verb `bin/tingle` always prepends) and forward `argv[2:]` to the orchestrator — the same contract `python/check_file_size/main.py` follows.
- No other agent depends on this package's internals beyond that entrypoint contract.

## Steps

- [01 — Scaffold the kube package and dispatcher entrypoint](python/01-scaffold-kube-package.md)
- [02 — Build the subcommand-aware parser](python/02-subcommand-parser.md)
- [03 — Define the config schema and defaults](python/03-config-schema-defaults.md)
- [04 — Implement the config loader with pass-through fallback](python/04-config-loader.md)
- [05 — Wire the executor and add unit tests](python/05-executor-and-tests.md)

## CI Checks
- `python/`: `ruff check .` (CI job: `lint`)
- `python/`: `pytest` (CI job: `tests`)

## Notes
- Every subcommand (`switch`, `list`, `shell`, `configure`) is stub/no-op behavior in this issue — real logic starts in child issues #21-#24 (Context, Discovery, Execution, Configuration respectively). Keep each subcommand's handler as a clearly-marked placeholder (e.g. a short "not yet implemented" message) rather than leaving it silently doing nothing, so manual testing during review is unambiguous.
