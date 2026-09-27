# `tingle linux`

A GNU/Linux toolbox (GNU `sed`, and a shell with git, kubectl, aws, ...)
that runs inside a container.

## What it does

Some command-line tools on your machine behave differently from their
GNU/Linux versions. For example, macOS ships BSD `sed`, where `-i` needs a
backup-suffix argument (`sed -i '' 's/a/b/' file`), while GNU `sed` takes
`-i` on its own. Differences like this break scripts and muscle memory.

`tingle linux` runs the real GNU/Linux tools inside a Docker container,
against the files in your current directory, so you get the same behaviour
you would get on Linux.

- `tingle linux sed` runs GNU `sed` directly.
- `tingle linux shell` gives you a ready-made Linux workstation: a `bash`
  shell with git, ssh, jq, kubectl, the AWS CLI and many other tools (see
  [What's inside the shell](#whats-inside-the-shell)). It works against
  your files and, unless you ask for an isolated shell, your host's git,
  ssh, Kubernetes and AWS configuration.

## Prerequisites

- Docker installed, with the Docker daemon running.
- The container image `darthjee/tingle:<version>` is pulled automatically
  the first time you use the command. The image is about 200 MB to
  download, so the first run takes noticeably longer. Later runs reuse the
  local copy.

## Usage

```bash
tingle linux shell [--isolated]
tingle linux sed <sed-args...>
```

If you enabled bash completion with `tingle install`, pressing Tab completes
the `shell` and `sed` subcommands, the `--isolated` option after
`tingle linux shell`, and file and folder names for `sed` arguments.

## `tingle linux shell`

```bash
tingle linux shell [--isolated]
```

Opens an interactive `bash` shell (with a terminal attached) inside the
container, in your current directory. From there you can run any of the
bundled tools directly against your files. Type `exit` to leave the shell
and return to your host.

By default the shell also brings in your host's git, ssh, Kubernetes and
AWS configuration (see
[What the shell brings in from your host](#what-the-shell-brings-in-from-your-host)).
Pass `--isolated` to skip that (see
[Opting out: `--isolated`](#opting-out---isolated)). `--isolated` is the
only option `shell` accepts.

Before the shell starts, a one-line banner is printed to standard error
with the image version and a summary of the bundled tools, for example:

```text
tingle linux 0.1.0 — git, ssh, jq, curl, wget, vim, rg, fd, bat, tmux, make, kubectl, aws, ... (full list: docs/guides/linux.md)
```

When the shell is isolated, the banner ends with ` (isolated)`. Because
the banner goes to standard error, it doesn't mix with anything you
redirect from standard output.

## What's inside the shell

The tools below are available inside `tingle linux shell`. Apart from
`sed`, which also has its own subcommand (`tingle linux sed`), they are
only usable from within the shell; there is no `tingle linux <tool>`
shortcut for them.

### GNU baseline

- coreutils — the standard GNU `ls`, `cp`, `mv`, `cat`, `sort`, `date`, ...
- findutils — GNU `find` and `xargs`.
- `grep` — search text with GNU regular expressions.
- GNU `sed` — stream editor, with GNU `-i` in-place syntax.
- `gawk` — GNU `awk` for column-oriented text processing.
- `tar` — create and extract tar archives.
- diffutils (`diff`, `cmp`) — compare files line by line or byte by byte.

### git & ssh

- `git` — version control.
- `ssh` / `scp` / `ssh-add` / `ssh-keygen` (openssh-client) — connect to
  remote hosts, copy files over SSH, and manage agent keys.

### data & network

- `jq` — query and reshape JSON.
- `curl` — make HTTP requests and download files.
- `wget` — download files from the web.
- `dig` (dnsutils) — look up DNS records.
- `ping` (iputils-ping) — check whether a host is reachable.
- `nc` (netcat-openbsd) — open raw TCP/UDP connections and test ports.
- `ip` (iproute2) — inspect network interfaces and routes.

### search & viewing

- `rg` (ripgrep) — fast recursive text search.
- `fd` (fd-find) — fast, friendly alternative to `find`.
- `bat` — `cat` with syntax highlighting and line numbers.
- `less` — page through long output or files.
- `tree` — show a directory as a tree.
- `file` — identify a file's type.
- `vim` — text editor.

`fd` and `bat` work under those names. Debian-based systems normally
install them as `fdfind` and `batcat`; the image adds `fd` and `bat`
shortcuts for you.

### dev & archives

- `make` — run Makefile targets.
- `shellcheck` — lint shell scripts.
- `bc` — command-line calculator.
- `rsync` — copy and synchronise files efficiently.
- `zip` / `unzip` — create and extract zip archives.
- `xz` (xz-utils) — compress and decompress `.xz` files.

### terminal

- `bash` with bash-completion — the shell itself, with Tab completion.
- `tmux` — split the terminal and run several sessions.
- `htop` — interactive process viewer.
- `ps` (procps) — list running processes.

### Kubernetes & AWS

- `kubectl` — manage Kubernetes clusters.
- `aws` (AWS CLI v2) — manage AWS resources from the command line.

## What the shell brings in from your host

Unless you use `--isolated`, `tingle linux shell` passes the following into
the container. Each item is only passed when it exists on your host (the
file or folder is there, the variable is set and non-empty, ...);
anything missing is silently skipped.

| Area | What is passed | Access |
| --- | --- | --- |
| git | `~/.gitconfig` and `~/.config/git/` | read-only |
| ssh | your SSH agent: Docker Desktop's forwarded agent socket, or `$SSH_AUTH_SOCK` on native Docker on Linux | agent access |
| ssh | `~/.ssh/config` and `~/.ssh/known_hosts` | read-only |
| kube | the first existing file in `$KUBECONFIG` (default `~/.kube/config`) | read-write |
| aws | `~/.aws/` | read-write |
| aws | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_PROFILE`, `AWS_REGION`, `AWS_DEFAULT_REGION` (each only if non-empty) | environment variables |
| network | host networking (`--network host`), on native Docker on a Linux host only | shared network |

A few things to know:

- **Private SSH keys are never mounted.** SSH authentication inside the
  container goes through your SSH agent, so load your keys into the agent
  on your host (`ssh-add`) before opening the shell.
- **git's credential helper is reset** inside the container. Your host
  `~/.gitconfig` may name a helper that doesn't exist in the image (for
  example `osxkeychain` on macOS); tingle clears it so git doesn't try to
  run it.
- **Read-write mounts change your host files.** Switching Kubernetes
  context (`kubectl config use-context ...`) or logging in with
  `aws sso login` inside the shell updates your real kubeconfig and
  `~/.aws/` on the host. Use `--isolated` if you don't want that.
- **Host networking** is only used with native Docker on a Linux host,
  where it lets the shell reach services on the host's `127.0.0.1` and
  your VPN routes. It is never used with Docker Desktop. This mode, and
  the `$SSH_AUTH_SOCK` agent forwarding on native Linux Docker, follow the
  rules described here but haven't been tested end to end.

### Opting out: `--isolated`

To open a shell without any host configuration, use either of:

```bash
tingle linux shell --isolated
TINGLE_LINUX_ISOLATED=1 tingle linux shell
```

The variable must be exactly `1`; any other value (or leaving it unset)
means not isolated. An isolated shell gets no git, ssh, kube or aws
config, no SSH agent, no `AWS_*` variables and no host networking. Only
your current directory is mounted, just like `tingle linux sed`.

### Security notes

- Any process running inside the shell can use the credentials you pass
  in: your SSH agent, AWS keys and session tokens, and your kubeconfig.
  Only run tools you trust, or use `--isolated`.
- `AWS_*` values are not put on the `docker run` command line, but they
  are stored in the container's configuration, so anyone who can run
  `docker inspect` on your host can see them while the container exists.
- On a Linux host with native Docker, `--network host` shares your host
  network with the container, including services listening on
  `127.0.0.1` and VPN routes.

### Known limitations

- Files that your config includes from elsewhere aren't mounted: ssh
  `Include` files, git `[include]` paths, and kubeconfig files beyond the
  first one.
- Kubeconfig exec plugins, and certificate or key paths that point at
  host paths, won't resolve inside the container unless those paths are
  inside your current directory.
- Only the first `KUBECONFIG` path is used; several kubeconfig files are
  not merged.
- Clusters on `127.0.0.1` (for example a local kind or minikube cluster)
  aren't reachable from Docker Desktop on macOS. Point the server at
  `host.docker.internal` instead, either in a copy of the kubeconfig or
  with `kubectl --server https://host.docker.internal:<port>`. The
  cluster's TLS certificate may not include that name, so verification
  can fail.
- `aws sso login` can't open a browser on your host from inside the
  container. Use `aws sso login --use-device-code` and open the printed
  link yourself.

## `tingle linux sed`

```bash
tingle linux sed <sed-args...>
```

Runs GNU `sed` inside the container. All arguments are passed to `sed`
unchanged. Standard input is attached (without a terminal), so you can use
it both on files and in pipelines. `sed` never brings in host
configuration and prints no banner.

Edit a file in place, using GNU `-i` syntax (no backup-suffix argument,
unlike BSD `sed`):

```bash
tingle linux sed -i 's/foo/bar/' somefile.txt
```

Pipe standard input through GNU `sed`; the result is written to standard
output:

```bash
cat file | tingle linux sed 's/a/b/'
```

## How your files are mounted

- Your current directory is mounted into the container at the same path
  and used as the working directory, so relative paths behave exactly as
  they do on your host.
- For `tingle linux sed` and `tingle linux shell --isolated`, only the
  current directory (and everything below it) is visible inside the
  container. A path such as `../other.txt`, or an absolute path outside
  the current directory, will not be found. If you need files from several
  places, `cd` to a common parent directory first.
- A plain `tingle linux shell` also mounts the host configuration listed
  in [What the shell brings in from your host](#what-the-shell-brings-in-from-your-host);
  other files outside the current directory are still not visible.
- The container runs as your host user and group IDs, so files it creates
  or edits stay owned by you.
- Each run uses a fresh container that is removed when the command ends.
  Only changes made inside the mounted directory (and, for a plain
  `shell`, the read-write kubeconfig and `~/.aws/` mounts) are kept.

## Errors

- Running `tingle linux` without a subcommand, or with an unknown one,
  prints this to standard error and exits with status 1:

  ```text
  tingle linux: unknown subcommand '<name>'
  ```

  When no subcommand is given, `<name>` is empty (`''`).

- Passing `tingle linux shell` anything other than `--isolated` prints
  this to standard error and exits with status 1:

  ```text
  tingle linux shell: unknown option '<arg>'
  ```

- If Docker is not installed or the daemon is not running, the error
  message comes from `docker` itself.

## Quick help

For a short summary of the command, run:

```bash
tingle --help linux
```
