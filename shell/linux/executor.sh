#!/usr/bin/env bash
#
# executor.sh - Subcommand router for the `linux` command (flow verb
# protocol).
#
# Reads the subcommand name from $1 and dispatches to the matching handler
# function via a case statement. Each handler calls into docker_run (from
# docker_run.sh, sourced below) to run the real GNU/Linux tool inside the
# tingle-linux container.
#
# Usage:
#   tingle linux shell [--isolated]
#   tingle linux sed <sed-args...>
#
# shell brings the host's configuration into the container. Each item is
# added only when it applies (the host file exists, the variable is set,
# ...) and silently skipped otherwise:
#   - git: ~/.gitconfig and ~/.config/git/ (read-only), and the credential
#     helper reset through GIT_CONFIG_COUNT/KEY_0/VALUE_0 (so the host's
#     osxkeychain helper isn't used);
#   - ssh: the agent socket (Docker Desktop's /run/host-services/ssh-auth.sock,
#     with --group-add 0 because that socket is root:root 660; or
#     $SSH_AUTH_SOCK on a native Linux host), ~/.ssh/known_hosts and
#     ~/.ssh/config (read-only, as ~/.ssh/host_config, which the image
#     entrypoint includes). Private keys are never mounted;
#   - kube: the first existing file in ${KUBECONFIG:-~/.kube/config}
#     (read-write, as /home/tingle/.kube/config, with KUBECONFIG set);
#   - aws: ~/.aws/ (read-write) and the non-empty AWS_ACCESS_KEY_ID,
#     AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_PROFILE, AWS_REGION and
#     AWS_DEFAULT_REGION (passed by name, so values never appear on the
#     command line);
#   - network: --network host on native Docker on a Linux host (not Docker
#     Desktop), so clusters on 127.0.0.1 are reachable.
# `--isolated`, or TINGLE_LINUX_ISOLATED=1 (exactly 1), skips all of it,
# including the `docker info` detection. shell also prints a one-line banner
# to stderr (image version and main tools, plus "(isolated)" when isolated);
# sed never does.
#
# Dependencies: docker_run.sh and VERSION in the same directory; docker
#   (including `docker info` for Docker Desktop detection); uname.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./docker_run.sh
source "$SCRIPT_DIR/docker_run.sh"

# Main tools in the image, shown in the shell banner. Keep in sync with
# shell/linux/Dockerfile by hand.
LINUX_TOOLS="git, ssh, jq, curl, wget, vim, rg, fd, bat, tmux, make, kubectl, aws, ..."

CONTAINER_HOME="/home/tingle"
DOCKER_DESKTOP_SSH_SOCK="/run/host-services/ssh-auth.sock"
AWS_ENV_NAMES="AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE AWS_REGION AWS_DEFAULT_REGION"

# Prints the one-line banner to stderr. $1 is "true" when isolated.
_banner() {
    local suffix=""
    [ "$1" = true ] && suffix=" (isolated)"
    echo "tingle linux $(tr -d '[:space:]' < "$SCRIPT_DIR/VERSION") — $LINUX_TOOLS (full list: docs/guides/linux.md)$suffix" >&2
}

# Succeeds when the Docker daemon is Docker Desktop (on any host OS). A
# failing `docker info` counts as "not Docker Desktop".
_docker_desktop() {
    local os
    os=$(docker info --format '{{.OperatingSystem}}' 2>/dev/null) || return 1
    case "$os" in
        *"Docker Desktop"*) return 0 ;;
        *) return 1 ;;
    esac
}

# Prints the first colon-separated entry of ${KUBECONFIG:-~/.kube/config}
# that is an existing file, or nothing.
_kubeconfig_path() {
    local rest="${KUBECONFIG:-$HOME/.kube/config}:"
    local entry
    # Split by hand (no word splitting), so paths with spaces or glob
    # characters are safe.
    while [ -n "$rest" ]; do
        entry="${rest%%:*}"
        rest="${rest#*:}"
        if [ -n "$entry" ] && [ -f "$entry" ]; then
            echo "$entry"
            return 0
        fi
    done
}

# Fills the global SHELL_ARGS array with the host-integration docker-args.
_shell_args() {
    SHELL_ARGS=()

    local desktop=false
    _docker_desktop && desktop=true
    local host_os
    host_os=$(uname -s)

    # git
    if [ -f "$HOME/.gitconfig" ]; then
        SHELL_ARGS+=(-v "$HOME/.gitconfig:$CONTAINER_HOME/.gitconfig:ro")
    fi
    if [ -d "$HOME/.config/git" ]; then
        SHELL_ARGS+=(-v "$HOME/.config/git:$CONTAINER_HOME/.config/git:ro")
    fi
    SHELL_ARGS+=(-e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=credential.helper -e GIT_CONFIG_VALUE_0=)

    # ssh agent: Docker Desktop's socket only exists inside its VM, so it
    # isn't checked on the host. It is root:root with mode 660, so the host
    # uid also gets supplementary group 0 (the only root-group-writable paths
    # in the image are already mode 1777, and there are no setuid files).
    if [ "$desktop" = true ]; then
        SHELL_ARGS+=(-v "$DOCKER_DESKTOP_SSH_SOCK:$DOCKER_DESKTOP_SSH_SOCK" -e "SSH_AUTH_SOCK=$DOCKER_DESKTOP_SSH_SOCK" --group-add 0)
    elif [ "$host_os" = Linux ] && [ -S "${SSH_AUTH_SOCK:-}" ]; then
        SHELL_ARGS+=(-v "$SSH_AUTH_SOCK:$SSH_AUTH_SOCK" -e "SSH_AUTH_SOCK=$SSH_AUTH_SOCK")
    fi

    # ssh config (never keys or the ~/.ssh directory)
    if [ -f "$HOME/.ssh/known_hosts" ]; then
        SHELL_ARGS+=(-v "$HOME/.ssh/known_hosts:$CONTAINER_HOME/.ssh/known_hosts:ro")
    fi
    if [ -f "$HOME/.ssh/config" ]; then
        SHELL_ARGS+=(-v "$HOME/.ssh/config:$CONTAINER_HOME/.ssh/host_config:ro")
    fi

    # kube (read-write, so context switches persist to the host)
    local kubeconfig
    kubeconfig=$(_kubeconfig_path)
    if [ -n "$kubeconfig" ]; then
        SHELL_ARGS+=(-v "$kubeconfig:$CONTAINER_HOME/.kube/config" -e "KUBECONFIG=$CONTAINER_HOME/.kube/config")
    fi

    # aws (read-write, for SSO/CLI caches); env passed by name only
    if [ -d "$HOME/.aws" ]; then
        SHELL_ARGS+=(-v "$HOME/.aws:$CONTAINER_HOME/.aws")
    fi
    local name
    for name in $AWS_ENV_NAMES; do
        if [ -n "${!name:-}" ]; then
            SHELL_ARGS+=(-e "$name")
        fi
    done

    # network: native Docker on Linux only
    if [ "$host_os" = Linux ] && [ "$desktop" != true ]; then
        SHELL_ARGS+=(--network host)
    fi
}

_handle_shell() {
    local isolated=false
    [ "${TINGLE_LINUX_ISOLATED:-}" = 1 ] && isolated=true

    local arg
    for arg in "$@"; do
        case "$arg" in
            --isolated)
                isolated=true
                ;;
            *)
                echo "tingle linux shell: unknown option '$arg'" >&2
                exit 1
                ;;
        esac
    done

    _banner "$isolated"

    if [ "$isolated" = true ]; then
        docker_run tty -- bash
        return
    fi

    _shell_args
    docker_run tty ${SHELL_ARGS[@]+"${SHELL_ARGS[@]}"} -- bash
}

_handle_sed() {
    docker_run stdin -- sed "$@"
}

subcommand="${1:-}"
[ -n "$subcommand" ] && shift

case "$subcommand" in
    shell)
        _handle_shell "$@"
        ;;
    sed)
        _handle_sed "$@"
        ;;
    *)
        echo "tingle linux: unknown subcommand '$subcommand'" >&2
        exit 1
        ;;
esac
