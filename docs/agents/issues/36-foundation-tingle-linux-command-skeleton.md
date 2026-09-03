# Issue: Foundation: tingle linux command skeleton

## Description
Lays the foundation for `tingle linux` (parent #34): the command dispatcher
under `shell/linux/` and the shared `docker run` invocation wrapper that
every future subcommand (`shell`, `sed`, and any GNU tool added later)
builds on. Depends on sub-issue #35 (image build/publish, already merged),
which published the `darthjee/tingle` image this skeleton wires a reference
to.

## Problem
`tingle linux` has no entry point yet. Before `shell`/`sed` (or any future
subcommand) can be implemented, the repo needs the standard
`<language>/<command>/main.<ext>` dispatcher, a subcommand executor that
routes to per-subcommand handlers (mirroring `python/kube/executor.py`'s
`_handlers` map), and one shared helper implementing the agreed `docker run`
invocation model so no subcommand hand-rolls its own container invocation.

## Expected Behavior
- `shell/linux/main.sh` follows the flow-verb dispatcher convention (like
  `shell/install/main.sh`), forwarding `run` to `shell/linux/executor.sh`.
- `shell/linux/executor.sh` reads the subcommand name from argv and
  dispatches to a per-subcommand handler map with `shell` and `sed` entries
  wired in, each calling a no-op stub (e.g. prints a not-implemented
  message) — proves the dispatch wiring end-to-end even though the real
  behavior lands in #37/#38.
- A shared helper (`shell/linux/docker_run.sh`, or a function in
  `executor.sh`) implements:
  ```
  docker run --rm [-it] \
    --user "$(id -u):$(id -g)" \
    -v "$(pwd):$(pwd)" \
    -w "$(pwd)" \
    <tingle-linux-image> <command-and-args...>
  ```
  with the `-it` flag toggleable per call, since `shell` needs it and `sed`
  does not.
- `commands/shell.json` gets a `linux` entry (`short_help`/`long_help`),
  following the `install`/`check_file_size` entries' format.
- The image reference from `docs/agents/tingle-linux-image.md` is wired into
  the helper as a hardcoded constant: `darthjee/tingle:0.0.1` (no `v*` tag
  has actually been published yet; update this constant once a real release
  tag exists).

## Solution
- `shell/linux/main.sh` — thin dispatcher, same shape as
  `shell/install/main.sh`.
- `shell/linux/executor.sh` — subcommand router with a handler map
  containing `shell`/`sed` entries backed by no-op stubs; their real
  behavior lands in #37/#38.
- `shell/linux/docker_run.sh` — the shared container-invocation helper,
  taking the interactive toggle and the command/args to run inside the
  container as parameters.
- `commands/shell.json` — add the `linux` entry pointing at
  `shell/linux/main.sh`.

### Out of scope
- Implementing `shell` or `sed` themselves (#37, #38) — only the dispatch
  scaffolding and shared docker-run helper.
