# Guide Plan: linux: user docs, Docker Hub descriptions and release 0.1.0

Main plan: [plan.md](plan.md)

## Shared contracts

- Use the **grouped tool list** from [plan.md](plan.md#shared-contracts)
  verbatim (seven groups, same order and names), each tool with a one-line
  purpose.
- The list must sit under the exact heading `## What's inside the shell`
  (anchor `#whats-inside-the-shell`). `DOCKERHUB_DESCRIPTION.md` links to it.
- You measure the image pull size (Step 1) and state it in Prerequisites.

## Implementation Steps

### Step 1 — Intro, Prerequisites and "What's inside the shell"
- Intro line and "What it does": the command is now a GNU/Linux toolbox, not
  just GNU `sed`/shell. Keep the BSD-vs-GNU `sed` example, and add that
  `tingle linux shell` gives a ready Linux workstation (git, kubectl, aws, ...)
  against your files and your host config.
- Prerequisites: the first pull is larger. Measure it: build the image from
  `main` for the host architecture
  (`docker buildx build -f shell/linux/Dockerfile --load -t tingle-size .`),
  then approximate the compressed pull size with
  `docker save tingle-size | gzip | wc -c`. Round to the nearest 50 MB and
  write "about N MB". If Docker isn't available, keep "about 500 MB" and
  say so in the PR description.
- New `## What's inside the shell` section: the seven groups as sub-lists,
  one line of purpose per tool (for example "`jq` — query and reshape JSON").
  Mention that `fd` and `bat` work under those names (the image adds the
  symlinks), and that tools are also usable through `tingle linux shell`
  only. `sed` is the only direct subcommand.

### Step 2 — Host integration, `--isolated`, security and limitations
Source of truth: `docs/agents/tingle-linux-image.md` → "`shell` host
integration", and `linux.long_help` in `commands/shell.json`. Write for users,
not implementers.
- Update the `## tingle linux shell` section: usage
  `tingle linux shell [--isolated]`, and the one-line stderr banner
  (version + tool summary, `(isolated)` suffix).
- New section (for example `## What the shell brings in from your host`): a
  table or list of what is mounted/passed and when (each item only if it
  exists on the host):
  - git: `~/.gitconfig` and `~/.config/git/` read-only; the credential helper
    is reset inside the container;
  - ssh: the SSH agent (Docker Desktop's forwarded socket, or
    `$SSH_AUTH_SOCK` on native Linux Docker), `~/.ssh/config` and
    `~/.ssh/known_hosts` read-only; private keys are never mounted;
  - kube: the first existing file in `$KUBECONFIG` (default
    `~/.kube/config`), read-write;
  - aws: `~/.aws/` read-write, plus any non-empty `AWS_ACCESS_KEY_ID`,
    `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_PROFILE`,
    `AWS_REGION`, `AWS_DEFAULT_REGION`;
  - network: `--network host` on native Docker on a Linux host only.
  Say that read-write mounts mean context switches and SSO logins change your
  host files.
- `### Opting out: --isolated`: `tingle linux shell --isolated` or
  `TINGLE_LINUX_ISOLATED=1` (exactly `1`) skips all of the above.
- `### Security notes`:
  - any process in the shell can use the passed credentials (agent, AWS keys,
    kubeconfig);
  - values passed with `-e` are visible to `docker inspect` on the host
    (they're not on the `docker run` command line, but they are in the
    container config);
  - `--network host` on Linux shares the host network (services on
    `127.0.0.1`, VPN routes).
- `### Known limitations`:
  - files included from your config (ssh `Include`, git `[include]`
    paths, kubeconfig files beyond the first) aren't mounted;
  - kubeconfig exec plugins or certificate/key paths that point at host
    paths won't resolve unless those paths are inside the current directory;
  - only the first `KUBECONFIG` path is used (no merging);
  - clusters on `127.0.0.1` aren't reachable from Docker Desktop on macOS:
    point the server at `host.docker.internal` instead (in a copy of the
    kubeconfig, or with `kubectl --server`), noting TLS names may not match;
  - `aws sso login` can't open a host browser from the container: use
    `aws sso login --use-device-code`.
- Update `## How your files are mounted`: the "only the current directory is
  visible" point now holds for `sed` and `shell --isolated`; the plain
  `shell` also mounts the host config listed above.
- `docs/guides/README.md`: update the `linux` one-liner, for example
  "GNU/Linux toolbox (sed, shell with git, kubectl, aws, ...) in a container."

## Files to Change
- `docs/guides/linux.md` — intro, Prerequisites (measured size), "What's inside the shell", host integration, `--isolated`, security notes, known limitations, mounts section
- `docs/guides/README.md` — `linux` index line

## CI Checks
- Markdown is checked by Codacy (markdownlint): real headings (not bold text),
  no raw HTML such as `<kbd>`, fenced code blocks with a language where the
  rest of the guide uses one.

## Notes
- Don't claim things parts 1–3 didn't verify. Native Linux Docker
  (`--network host`, `$SSH_AUTH_SOCK`) is only stub-tested, so describe the
  behaviour without promising it was tested end to end.
