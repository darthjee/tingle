# Add the apt toolbox and fd/bat symlinks

Add these packages to the final stage's single apt `RUN`, each pinned to its exact version at `UBUNTU_SNAPSHOT` and checked on both architectures:

- git and friends: `git`, `ca-certificates`, `openssh-client`, `less`
- data and network: `jq`, `curl`, `wget`, `dnsutils`, `iputils-ping`, `netcat-openbsd`, `iproute2`
- editing, search and viewing: `vim`, `ripgrep`, `fd-find`, `bat`, `bash-completion`, `tree`, `file`
- archives and dev: `unzip`, `zip`, `xz-utils`, `bc`, `make`, `shellcheck`, `rsync`
- terminal and processes: `procps`, `tmux`, `htop`

Keep the existing 7 packages. Group the list with the comments above, alphabetical within each group, so later diffs are easy to review.

In the same `RUN`, after the install, create the symlinks:

```bash
ln -s /usr/bin/fdfind /usr/local/bin/fd
ln -s /usr/bin/batcat /usr/local/bin/bat
```

Put this layer after the base and before the upstream-tool `COPY`s, so bumping `kubectl` or `aws` doesn't invalidate it.

Check that every command in the plan.md smoke-check table (except `kubectl` and `aws`) passes as the `tingle` user. Watch out for `ping -V` (iputils) and `dig -v` (it prints to stderr, so check its exit code). Report any command that has to change.

## Files to Change
- `shell/linux/Dockerfile` — pinned toolbox packages and the `fd`/`bat` symlinks in the apt `RUN`.
