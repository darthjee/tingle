# Issue: Execution: sed subcommand

## Description
Wire the `sed` subcommand into `tingle linux` (parent: #34 — `Add tingle linux`). This is the original motivating use case for the `linux` command: running GNU `sed` (not macOS's BSD `sed`) against files in the current directory.

The command skeleton (#36) and shared `docker_run` helper already exist. `_handle_sed` in `shell/linux/executor.sh` is currently a stub that errors with "not implemented yet (see issue #38)".

## Expected Behavior
- `tingle linux sed <args...>` forwards to GNU sed inside the container, dispatched through the existing `linux` command skeleton exactly like `tingle linux shell`.
- `cat file | tingle linux sed 's/a/b/'` works — stdin is piped through to `sed` inside the container without allocating a TTY.
- Manual verification: from a repo directory, run `tingle linux sed -i 's/foo/bar/' somefile.txt` using GNU `-i` syntax (no backup-suffix argument, unlike BSD `sed`) — confirm the file is edited in place and owned by the host user afterward. Also verify the piped-stdin case above produces the expected output.

## Solution
- Implement `_handle_sed` in `shell/linux/executor.sh`: call `docker_run`, forwarding all remaining arguments verbatim to `sed` inside the `tingle-linux` container — no parsing or validation of `sed`'s own flags, pure passthrough.
- Extend `docker_run` (`shell/linux/docker_run.sh`) with a third stdin-only mode: today it only supports `-it` (interactive=true) or neither (interactive=false), which means piped stdin currently has nothing attached and would hang/fail. Add a mode that passes `-i` alone (attach stdin, no TTY) so `cat file | tingle linux sed 's/a/b/'` works. `_handle_sed` uses this new stdin-only mode; `_handle_shell`'s existing `-it` usage is unaffected.
- No TTY (`-it`) is needed for `sed` itself — it's normally non-interactive; only stdin needs to be attached.
- Add usage/examples for `sed` to `commands/shell.json`'s `long_help` for `linux` (an entry for `shell` already exists there as a model to follow), including a piped-stdin example.

### Out of scope
Any subcommand beyond `sed` — additional GNU tools can be added later following this same pattern.

### Dependencies
Depends on sub-issue #36 (command skeleton, already merged). Independent of the `shell` sub-issue (#37, already merged).
