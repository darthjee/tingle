# Python Plan: kube list pods: option to list all pods found in the server

Main plan: [plan.md](plan.md)

## Shared contracts

- Define `--all` (`store_true`, long form only) on the `pods` subparser with
  help `Also list pods that match no configured alias (within the given
  namespace)`; read it as `parsed.get("all")`.
- With `--all`, text output appends a final `(unmatched):` block (always
  printed) and never prints the "candidates discarded by id_pattern" hint;
  JSON appends `{"alias": null, "pods": [...]}` (always present).
- Unmatched = pods matched by none of the displayed aliases, ordered by
  `creationTimestamp` ascending.
- Without `--all`, text and JSON output must stay byte-for-byte identical.

## Steps

- [01 — Add the --all flag to the parser](python/01-parser-flag.md)
- [02 — Print unmatched pods in list pods](python/02-list-pods-unmatched.md)
- [03 — Complete --all in bash completion](python/03-completion.md)

## CI Checks

- `python/`: `ruff check .` (CI job: `lint`)
- `python/`: `pytest` (CI job: `tests`)

## Notes

- `docs/agents/` does not describe `list pods` behavior in detail, so no
  product-owner work is needed.
- The known limitations listed in the issue (namespace notice printed before
  JSON; alias namespace filter compares against the argument as typed) are out
  of scope — do not fix them here.
