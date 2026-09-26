# Extend docker_run and update its callers
In `shell/linux/docker_run.sh`, change the signature to `docker_run <mode> [docker-args...] -- <command> [args...]`:

- After the mode, collect arguments into a `docker_args` array until the first `--`. Everything after it is the command.
- If there is no `--`, print `docker_run: missing '--' before command` to stderr and return 1.
- Always add `--security-opt no-new-privileges` to the `docker run` invocation.
- Put `"${docker_args[@]}"` before the image name, after the built-in flags.
- Guard against empty-array expansion under `set -u`, matching how `tty_flags` is handled.
- Update the usage and header comments.

In `shell/linux/executor.sh`, update the callers to `docker_run tty -- bash` and `docker_run stdin -- sed "$@"`. Arguments that users pass to `sed`, including a literal `--`, must reach `sed` unchanged.

## Files to Change
- `shell/linux/docker_run.sh`: new signature, `no-new-privileges`, comments.
- `shell/linux/executor.sh`: callers pass `--`.
