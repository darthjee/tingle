# Add the docker_run helper

Create `shell/linux/docker_run.sh`, the shared container-invocation helper
every `tingle linux` subcommand builds on. It implements the model agreed in
#34:

```
docker run --rm [-it] \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):$(pwd)" \
  -w "$(pwd)" \
  darthjee/tingle:0.0.1 <command-and-args...>
```

Expose it as a function, `docker_run`, sourced by `executor.sh`:

```bash
# docker_run <interactive: true|false> <command> [args...]
docker_run() {
    local interactive="$1"
    shift

    local tty_flags=()
    if [ "$interactive" = "true" ]; then
        tty_flags=(-it)
    fi

    docker run --rm "${tty_flags[@]}" \
        --user "$(id -u):$(id -g)" \
        -v "$(pwd):$(pwd)" \
        -w "$(pwd)" \
        "$TINGLE_LINUX_IMAGE" "$@"
}
```

Define the image reference as a constant at the top of the file:

```bash
TINGLE_LINUX_IMAGE="darthjee/tingle:0.0.1"
```

Follow `shell/install/executor.sh`'s header-comment style (usage,
dependencies) and `set -euo pipefail`.

## Files to Change
- `shell/linux/docker_run.sh` (new) — the shared `docker_run` helper
  function and the `TINGLE_LINUX_IMAGE` constant.
