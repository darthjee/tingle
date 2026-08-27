# Product-Owner Plan: Add command auto complete

Main plan: [plan.md](plan.md)

## Shared contracts

- Documents contracts 1–5 from [plan.md](plan.md) as the new command entrypoint convention, superseding the current single-file `<command>.<ext>` convention described in `docs/agents/architecture.md`.

## Implementation Steps

### Step 1 — Update the command entrypoint convention in `docs/agents/architecture.md`

Replace the description of a command's entry point (currently
`<language>/<command>/<command>.<extension>`, e.g. `check_file_size.py`
holding the `CheckFileSize` orchestrator) with the new
`<language>/<command>/main.<extension>` dispatcher convention:

- `main.<ext>` is the file `commands/*.json` points at; it reads a leading
  `run`/`complete` flow verb (argv[1] / `$1`) and dispatches to either the
  executor (`//executor.<ext>`) or the completion handler
  (`//completion.<ext>`), never typed by the user — prepended by `bin/tingle`
  / the completion hub.
- Completion is opt-in per command: the hub detects it by whether
  `completion.<ext>` exists next to `main.<ext>`, not by invoking the
  command. Commands without one (e.g. `check_file_size`, `install`) get the
  hub's generic native file/folder completion fallback instead.
- A completion handler receives raw argv, including a possibly-empty
  trailing element for the word being typed, and must not run it through a
  strict parser (e.g. `argparse`).
- Update the `python/check_file_size/` worked example to reflect the new
  `main.py` + `executor.py` split (no `check_file_size.py` orchestrator file
  anymore).

### Step 2 — Update the `completions/` description in `docs/agents/architecture.md` and `docs/agents/folder-structure.md`

Both currently describe `completions/` as a single file,
`completions/tingle.bash`. Update both to describe the post-split shape:

- `completions/tingle.bash` — central hub, sources the two files below and
  registers the `complete -F` dispatcher.
- `completions/bash/tingle.sh` — level-one completion (command names).
- `completions/bash/commands.sh` — level-two completion (delegates to a
  command's own `completion.<ext>` via `tingle resolve <cmd>`, or falls back
  to native file/folder completion).

## Files to Change

- `docs/agents/architecture.md` — command entrypoint convention rewritten for `main.<ext>`/`executor.<ext>`/`completion.<ext>`; `check_file_size` worked example updated; `completions/` description updated.
- `docs/agents/folder-structure.md` — `completions/` row updated to describe the split.

## Notes

- `cli.md`'s Notes flag a scope gap: no agent explicitly owns `completions/` in `.claude/agents/`. Consider a follow-up (outside this issue) to add it to `cli`'s documented scope in `.claude/agents/cli.md` and `architect.md`'s specialist table, since this plan treats it as `cli`'s.
