# shell Plan: Execution: shell subcommand (the anchor command)

Main plan: [plan.md](plan.md)

## Shared contracts

- Must implement exactly `tingle linux shell` (no arguments) as an
  interactive shell, matching the usage example `cli` documents in
  `commands/shell.json`.

## Implementation Steps

### Step 1 — Wire `_handle_shell` to `docker_run`

In `shell/linux/executor.sh`, replace the `_handle_shell` stub (which
currently just prints "not implemented yet" and exits 1) with a call to the
`docker_run` helper already sourced at the top of the file:

```bash
_handle_shell() {
    docker_run true bash
}
```

`docker_run`'s existing behavior (from `shell/linux/docker_run.sh`) already
covers everything the issue asks for: `-it` when `interactive=true`, the cwd
mounted and set as the working dir, running as `$(id -u):$(id -g)` so
files stay host-owned, and `--rm` so no container lingers after exit — no
changes needed there.

## Files to Change

- `shell/linux/executor.sh` — replace the `_handle_shell` stub with
  `docker_run true bash`.

## Notes

- Manual verification (not automatable in CI): run `tingle linux shell` from
  a repo directory and confirm (1) the cwd is mounted and browsable inside
  the shell, (2) files created/edited from the shell are owned by the host
  user after exiting, and (3) `docker ps -a` shows no lingering container
  after exiting.
