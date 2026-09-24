# Guide Plan: docs: add user guide for tingle linux (docs/guides/linux.md)

Main plan: [plan.md](plan.md)

## Overview
Write `docs/guides/linux.md` for end users and replace the `linux`
placeholder in `docs/guides/README.md` with a link to it.

## Context
`tingle linux` is registered in `commands/shell.json`.
`shell/linux/main.sh` (`run` flow) execs `shell/linux/executor.sh`, which
routes `shell` and `sed` to `docker_run` in `shell/linux/docker_run.sh`.
`docker_run` runs:

```
docker run --rm <-it|-i> --user "$(id -u):$(id -g)" \
  -v "$(pwd):$(pwd)" -w "$(pwd)" darthjee/tingle:<VERSION> <cmd> [args...]
```

The tag comes from `shell/linux/VERSION` (currently `0.0.2`).
`docs/guides/install.md` is the style reference: a title plus a one-line
summary, then sections like "What it does", "Prerequisites", "Usage" and
"Examples".

## Implementation Steps

### Step 1 — Write `docs/guides/linux.md`
Title `# \`tingle linux\``, then the `short_help` line ("Run GNU/Linux tools
(sed, shell) inside a container."). Sections:

- **Why / what it does**: host tools can differ from their GNU/Linux
  versions. For example, macOS ships BSD `sed`, whose `-i` needs a
  backup-suffix argument. `tingle linux` runs the real GNU tool in a Docker
  container against your files.
- **Prerequisites**: Docker installed and the daemon running. The image
  `darthjee/tingle:<version>` is pulled automatically on first use, so the
  first run may take longer. Don't link to `docs/agents/` and don't list
  the tools inside the image.
- **Usage**: `tingle linux shell`, `tingle linux sed <sed-args...>`.
- **`tingle linux shell`**: opens an interactive `bash` (with a TTY) in
  the container, in your current directory, where you can run Linux-native
  tools on your files. Type `exit` to leave.
- **`tingle linux sed`**: all arguments go to GNU `sed` unchanged. Stdin is
  attached (no TTY), so both of these work:
  - `tingle linux sed -i 's/foo/bar/' somefile.txt` (GNU `-i`, no suffix)
  - `cat file | tingle linux sed 's/a/b/'` (output goes to stdout)
- **How your files are mounted**:
  - The current directory is mounted at the same path and used as the
    working directory, so relative paths behave as they do on the host.
  - Only the current directory (and what's below it) is visible. `../x`,
    or an absolute path outside it, won't be found, so `cd` to a common
    parent first.
  - The container runs as your host uid:gid, so files it creates or edits
    stay owned by you.
  - Each run is a fresh container (`--rm`). Only changes inside the
    mounted directory are kept.
- **Errors**: a missing or unknown subcommand prints
  `tingle linux: unknown subcommand '<name>'` to stderr and exits 1.
  If Docker isn't running, the error comes from `docker` itself.
- Pointer: `tingle --help linux` for the short summary.

Keep the examples consistent with the `long_help` in `commands/shell.json`.

### Step 2 — Update `docs/guides/README.md`
Replace
`- \`linux\` — Run GNU/Linux tools (sed, shell) inside a container. *(guide coming soon)*`
with
`- [\`linux\`](linux.md) — Run GNU/Linux tools (sed, shell) inside a container.`

## Files to Change
- `docs/guides/linux.md` — new end-user guide.
- `docs/guides/README.md` — link the `linux` entry and drop *(guide coming soon)*.

## Notes
- No CI job covers `docs/` (CircleCI only lints and tests `python/`).
- Take the behaviour only from `shell/linux/*.sh`, `Dockerfile` and
  `VERSION`. `docs/agents/tingle-linux-image.md` is background only and
  must not be linked from the guide.
- The Docker Hub description of the image is tracked separately in #182.
  It's out of scope here.
