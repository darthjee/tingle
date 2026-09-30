# Guide Plan: code_check: scaffold tingle code_check and move check_file_size to code_check file_size

Main plan: [plan.md](plan.md)

## Shared contracts

- The command is `tingle code_check <subcommand>`. Today's only subcommand is `file_size`, with behaviour identical to
  today's `tingle check_file_size`.
- `tingle code_check`, `-h` and `--help` list the subcommands and exit 0. `-h <sub>` shows that subcommand's help.
  An unknown subcommand or a flag before the subcommand is an error with exit 1.
- The exit-code convention is 0 ok, 1 usage/config error, 2 check gate (`--fail-on`).
- The config stays in `~/.tingle/code_check/config.json`, with one top-level section per subcommand. The section is
  still named `check_file_size` in this issue, so do not change the config key text.
- `tingle check_file_size` still works, with no warning. The migration note comes in a later sub-issue of #279.
- Paths: `docs/guides/code_check.md`, `docs/guides/code_check/file_size.md`, and `docs/guides/check_file_size.md` (stub).
  The root `README.md` links the overview and the stub.

## Implementation Steps

### Step 1 — Move the guide and write the overview
- `git mv docs/guides/check_file_size.md docs/guides/code_check/file_size.md`, keeping its history. Replace
  `tingle check_file_size` with `tingle code_check file_size` throughout: the title, the prose at lines 8-9 (split
  across a line break), usage, option examples, config prose, output sample, `NO_COLOR`, Examples and CI snippets.
  Change `tingle --help check_file_size` to `tingle --help code_check`, or to `tingle code_check file_size --help`.
  Leave the bare `check_file_size` config section key (L354, 358, 369, 420, 450, 509) as it is. The guide has no
  relative file links, so the move breaks nothing.
- New `docs/guides/code_check.md`, a short overview covering:
  - what `code_check` is;
  - a subcommand table linking `code_check/file_size.md`;
  - the shared config file with one section per subcommand, whose keys are documented on each page;
  - the exit-code convention;
  - `tingle code_check`, `-h` and `-h <sub>` help behaviour;
  - quick help.

### Step 2 — Stub and index
- Recreate `docs/guides/check_file_size.md` as a stub of a few lines. It says the command moved to
  `tingle code_check file_size` (the old name still works) and links `code_check/file_size.md`.
- `docs/guides/README.md`: replace the `check_file_size` bullet with a `code_check` bullet linking `code_check.md`,
  with a nested `file_size` bullet linking `code_check/file_size.md`. Add a `check_file_size` bullet saying
  "moved to `code_check file_size`" and linking the stub.
- Check that every link in `docs/guides/README.md` and in the new pages resolves.

## Files to Change
- `docs/guides/check_file_size.md` → `docs/guides/code_check/file_size.md` — `git mv`, then update the command name.
- `docs/guides/code_check.md` — new overview.
- `docs/guides/check_file_size.md` — new stub.
- `docs/guides/README.md` — index update.

## Notes
- No CI checks links. Codacy runs markdownlint, so keep the heading and emphasis style consistent with the existing guides.
- The architect updates `.claude/agents/guide.md` Conventions to allow `<command>/<subcommand>.md` pages.
