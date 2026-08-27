# Cli Plan: Add command auto complete

Main plan: [plan.md](plan.md)

## Shared contracts

- Depends on `python` producing `python/check_file_size/main.py` and `shell` producing `shell/install/main.sh` before `commands/*.json` is updated to point at them (contract 2).
- Owns and exposes the `tingle resolve <cmd>` helper (contract 5) and the feature-detection-by-file-presence + generic fallback logic (contract 3).
- Prepends the flow verb unconditionally (contract 1) — this is only safe once both commands speak the new contract, which is why this agent's Step 2 (updating `commands/*.json`) should land together with `python`'s and `shell`'s work, not before it.

## Steps

- [01 — Prepend flow verb and add resolve helper to bin/tingle](cli/01-bin-tingle-flow-verb-and-resolve.md)
- [02 — Update commands/*.json entrypoint paths](cli/02-update-commands-json-paths.md)
- [03 — Split completions/tingle.bash and add level-two delegation](cli/03-split-completions.md)

## CI Checks

No lint/check command is configured for `bin/`/`completions/`/`commands/` yet (per `docs/agents/todo.md`).

## Notes

- `completions/` has no explicit owning agent in `.claude/agents/` (only `bin/`, `commands/`, `shell/`, `python/`, `node/`, `docs/agents/`, and root files are assigned). It is treated here as part of `cli`'s scope for this issue, since it is tightly coupled to `bin/tingle`'s resolution/dispatch logic that `cli` already owns. Flag this gap to `architect`/`product-owner` for a follow-up doc update (`.claude/agents/cli.md`'s scope table and `docs/agents/architecture.md`'s folder listing) — out of scope to fix as part of implementing this issue.
