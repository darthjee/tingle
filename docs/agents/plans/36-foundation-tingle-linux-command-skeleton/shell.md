# Shell Plan: Foundation: tingle linux command skeleton

Main plan: [plan.md](plan.md)

## Shared contracts

Produces the entry point path `shell/linux/main.sh` that `cli` wires into
`commands/shell.json` (`linux` entry). Surfaces two subcommands to `cli`'s
help text: `shell` and `sed`, both stubbed here (real behavior in #37/#38).

## Steps

- [01 — Add the docker_run helper](shell/01-add-docker-run-helper.md)
- [02 — Add the subcommand executor](shell/02-add-subcommand-executor.md)
- [03 — Add the main.sh dispatcher](shell/03-add-main-dispatcher.md)

## CI Checks

None configured yet for `shell/` (no lint/check job exists — see
`docs/agents/todo.md`'s outstanding shellcheck item, unrelated to this
issue).

## Notes

- Image reference: hardcode `darthjee/tingle:0.0.1` per the confirmed
  answer during discussion — no `v*` tag has actually been published yet,
  so this constant will need updating once a real release tag exists (see
  `docs/agents/tingle-linux-image.md`).
- Keep `docker_run.sh` a dumb wrapper: it takes the interactive toggle and
  the in-container command/args as parameters, and does not know about
  `shell`/`sed`-specific behavior — that stays in each subcommand handler
  (stub for now, real logic in #37/#38).
