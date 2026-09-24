# Issue: docs: add user guide for tingle linux (docs/guides/linux.md)

## Description
Part of #172. Adds the end-user guide for the `linux` command. The command
is registered in `commands/shell.json`. `shell/linux/main.sh` hands off
to `shell/linux/executor.sh`, which routes each subcommand to
`docker_run` in `shell/linux/docker_run.sh`. The foundation sub-issue
#174 has landed, so `docs/guides/`, the `docs/guides/README.md` index
(with a `linux` placeholder) and the `guide` agent all exist already.
#175 (`install` guide) set the pattern to follow.

## Problem
There is no user guide for `tingle linux`. Users only have the short
`long_help` text and the root README. `docs/guides/README.md` lists
`linux` as *(guide coming soon)*, and the root README Scripts-table row
for `linux` doesn't link anywhere.

## Expected Behavior
- `docs/guides/linux.md` exists and is written for end users. It covers:
  - Why the command exists: host tools can differ from their GNU/Linux
    versions (for example BSD `sed` on macOS vs GNU `sed`), which
    breaks scripts and habits.
  - Prerequisites: Docker must be installed and running. The image
    `darthjee/tingle:<version>` (the tag comes from `shell/linux/VERSION`)
    is pulled automatically the first time you run it.
  - `tingle linux shell`: opens an interactive `bash` shell in the
    container (`-it`), where you can run Linux-native tools on your files.
    The guide doesn't list the tools the image contains.
  - `tingle linux sed <args...>`: all arguments are passed to GNU `sed`
    unchanged. Stdin is attached (`-i`, no TTY), so both in-place edits
    (`sed -i 's/foo/bar/' file`, with no backup-suffix argument, unlike
    BSD) and piping (`cat file | tingle linux sed 's/a/b/'`) work.
  - How the working directory is mounted: the current directory is mounted
    at the same path and used as the working directory. This means
    relative paths work, but files outside the current directory
    (`../x`, or absolute paths elsewhere) can't be seen. The container
    runs as your host uid:gid, so edited files keep the right owner. Each
    run is a fresh container (`--rm`), so nothing is kept outside the
    mounted directory.
  - Errors: an unknown or missing subcommand prints
    `tingle linux: unknown subcommand '<name>'` and exits with status 1.
- The `linux` entry in `docs/guides/README.md` links to the guide instead
  of showing *(guide coming soon)*.
- The `linux` row of the root `README.md` Scripts table links to
  `docs/guides/linux.md`.
- The content matches the `long_help` in `commands/shell.json` and the
  real behaviour of `shell/linux/executor.sh` and `docker_run.sh`.

## Solution
- `guide` agent: write `docs/guides/linux.md` and update the `linux`
  entry in `docs/guides/README.md`.
- `architect`: link the `linux` row in the root `README.md` Scripts
  table to `docs/guides/linux.md`. This is a root file, so the `guide`
  agent must not edit it.
- Take all behaviour from `shell/linux/executor.sh`,
  `shell/linux/docker_run.sh`, `shell/linux/Dockerfile` and
  `shell/linux/VERSION`. `docs/agents/tingle-linux-image.md` is
  background for the writer only.

## Benefits
- macOS users (and others) get one clear page that explains how to run GNU
  tools on their files, including what the container can and can't see.
- The guide can be reached from both the guides index and the root README.
