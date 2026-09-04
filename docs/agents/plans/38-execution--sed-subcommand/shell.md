# shell Plan: Execution: sed subcommand

Main plan: [plan.md](plan.md)

## Shared contracts

Must implement exactly this invocation and behavior (see `plan.md` for
the full shared contract, which `cli`'s `commands/shell.json` update
documents):

- `tingle linux sed <sed-args...>` forwards all arguments verbatim to
  `sed` inside the `tingle-linux` container — no parsing/validation of
  `sed`'s own flags.
- Piped-stdin usage works: `cat file | tingle linux sed 's/a/b/'`.
- `tingle linux sed -i 's/foo/bar/' somefile.txt` edits the file in place
  (GNU `-i` syntax) and the result is owned by the host user.

## Implementation Steps

### Step 1 — Extend `docker_run` with a stdin-only mode

Replace `docker_run`'s current `interactive: true|false` first argument
(which only supports bundled `-it` or neither) with a three-value mode:
`none` (no `-i`, no `-t` — same as today's `false`), `tty` (`-it` — same
as today's `true`), and `stdin` (new: `-i` alone, attaching stdin without
allocating a TTY). Update the function's header comment/usage
accordingly. Update `_handle_shell`'s existing call from
`docker_run true bash` to `docker_run tty bash` so its behavior is
unchanged.

### Step 2 — Implement `_handle_sed`

Replace the `_handle_sed` stub (currently just prints "not implemented
yet" and exits 1) with a call to `docker_run stdin sed "$@"`, forwarding
all remaining arguments verbatim — no flag parsing/validation. Using
`stdin` mode unconditionally (rather than only when input is actually
piped) is safe: `sed` invocations that don't read from stdin (e.g.
in-place edits on a named file) are unaffected by stdin being attached.

## Files to Change

- `shell/linux/docker_run.sh` — change the `interactive` boolean
  parameter to a `mode` enum (`none`/`tty`/`stdin`); `stdin` passes `-i`
  alone (no `-t`).
- `shell/linux/executor.sh` — update `_handle_shell`'s `docker_run` call
  to use the new `tty` mode; implement `_handle_sed` to call
  `docker_run stdin sed "$@"`.

## Notes

- No CI job currently lints/tests `shell/` (`.circleci/config.yml`'s
  `lint`/`tests` jobs only cover `python/`), so no `## CI Checks` section
  applies here.
- Manual verification (from a repo directory, with the `tingle-linux`
  image built/available): run
  `tingle linux sed -i 's/foo/bar/' somefile.txt` and confirm the file is
  edited in place and owned by the host user; run
  `cat somefile.txt | tingle linux sed 's/a/b/'` and confirm the piped
  output is correct.
