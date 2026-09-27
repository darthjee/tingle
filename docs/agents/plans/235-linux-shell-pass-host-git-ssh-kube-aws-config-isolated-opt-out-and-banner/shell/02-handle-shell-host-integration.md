# Host integration, --isolated and banner in _handle_shell
Rewrite `_handle_shell` in `shell/linux/executor.sh`. Split it into small helper functions (for example `_linux_isolated`, `_docker_desktop`, `_shell_args`, `_banner`) so it stays readable.

1. **Parse arguments.** `--isolated` sets isolated. Any other argument prints `tingle linux shell: unknown option '<arg>'` to stderr and exits 1. `TINGLE_LINUX_ISOLATED=1` also sets isolated.
2. **Banner.** Print to stderr: `tingle linux $(cat "$SCRIPT_DIR/VERSION") — $LINUX_TOOLS (full list: docs/guides/linux.md)`, adding ` (isolated)` when isolated. `LINUX_TOOLS` is a constant near the top of the file, for example `git, jq, curl, vim, rg, fd, bat, kubectl, aws, ...`, with a comment saying to keep it in sync with `shell/linux/Dockerfile`. `_handle_sed` never prints it.
3. **Isolated:** run `docker_run tty -- bash` and stop. There is no `docker info` call.
4. **Otherwise**, build a `local args=()` array, quoting every path, because `$HOME` and `$(pwd)` may contain spaces:
   - **Docker Desktop detection**, done once: `docker info --format '{{.OperatingSystem}}' 2>/dev/null`, which matches when the output contains `Docker Desktop`. A failure counts as "not Docker Desktop".
   - **git:** if `~/.gitconfig` is a file, add `-v "$HOME/.gitconfig:/home/tingle/.gitconfig:ro"`. If `~/.config/git` is a directory, add `-v "$HOME/.config/git:/home/tingle/.config/git:ro"`. Always add `-e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=credential.helper -e GIT_CONFIG_VALUE_0=`.
   - **SSH agent:** under Docker Desktop, add `-v /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock -e SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock`. Otherwise, when `uname -s` is `Linux` and `[ -S "${SSH_AUTH_SOCK:-}" ]`, mount it at the same path and set `SSH_AUTH_SOCK` to it. Otherwise add nothing.
   - **SSH config:** if `~/.ssh/known_hosts` is a file, mount it read-only at `/home/tingle/.ssh/known_hosts`. If `~/.ssh/config` is a file, mount it read-only at `/home/tingle/.ssh/host_config`. Never mount keys or the `~/.ssh` directory.
   - **kube:** take the first colon-separated entry of `${KUBECONFIG:-$HOME/.kube/config}` that is an existing file. If there is one, add `-v "<path>:/home/tingle/.kube/config" -e KUBECONFIG=/home/tingle/.kube/config` (read-write).
   - **AWS:** if `~/.aws` is a directory, add `-v "$HOME/.aws:/home/tingle/.aws"` (read-write). For each of `AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE AWS_REGION AWS_DEFAULT_REGION` that is non-empty (use indirect expansion, `${!name:-}`), add `-e NAME` without the value.
   - **Network:** when `uname -s` is `Linux` and Docker Desktop is not detected, add `--network host`.
5. Run `docker_run tty ${args[@]+"${args[@]}"} -- bash`.

Checks during implementation (record the outcome in the PR description):
- **kubectl writes:** with `~/.kube` now writable, confirm that `kubectl config use-context` writes the single bind-mounted file in place and the change persists on the host. If kubectl renames over the file instead, which fails on a single-file bind mount, then for the default-path case (no `KUBECONFIG`, and `~/.kube/config` exists) mount the whole `~/.kube` directory instead.
- **ssh ownership:** confirm that ssh accepts the ownership and permissions of the included `host_config` on macOS (Docker Desktop's file sharing) and on Linux. If not, change `shell/linux/entrypoint.sh` to copy it into the generated config's directory instead of including it in place. That also changes the image, which is covered by the `0.0.3` bump.
- **Docker Desktop socket:** confirm that `/run/host-services/ssh-auth.sock` works for a non-root uid (`ssh-add -l`).

## Files to Change
- `shell/linux/executor.sh` — rewrite `_handle_shell`, add helpers and the `LINUX_TOOLS` constant, and update the header comment (usage `tingle linux shell [--isolated]`, `TINGLE_LINUX_ISOLATED`, dependencies `docker info`, `uname`).
- `shell/linux/entrypoint.sh` — only if the ssh ownership check fails.
