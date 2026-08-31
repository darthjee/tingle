"""
completion.py — Bash-completion candidate resolution for kube.

`commands.sh` invokes `main.py complete "${COMP_WORDS[@]:2}"` — the raw argv
starting at the subcommand, including a possibly-empty trailing element for
the word currently being typed — and filters the returned candidates by
prefix itself via `compgen -W ... -- "$cur"`. This module therefore returns
the *full* candidate set for whatever position the cursor is at; it must not
filter by prefix.

The trailing element is dropped before positional scanning (it is
in-progress input, not a committed argument) and the remaining tokens are
scanned positionally rather than parsed with `argparse` — an empty trailing
element would otherwise be significant/rejected by a strict parser. Flags
(`--json`, `--namespace <value>`) may appear before or after positional
tokens, mirroring `KubeArgParser`'s own tolerance for both orders.

Only `KubeConfig()` (a local file read) and `scope.detect_active_scope()`
(a single local `kubectl config current-context` call) are used for dynamic
candidates — never `inventory.list_namespaces()`/`inventory.list_pods()`
(live cluster/API queries), keeping every keystroke fast and side-effect-free.
"""

from __future__ import annotations

from kube import scope
from kube.config import KubeConfig

SUBCOMMANDS = ["switch", "list", "shell", "configure"]
LIST_TARGETS = ["namespace", "pods", "--json"]
CONFIGURE_TARGETS = ["context", "namespace", "pod"]


def complete(argv: list[str]) -> list[str]:
    """Return the full candidate set for the cursor position implied by `argv`."""
    committed = argv[:-1] if argv else []
    subcommand, positionals, _flags, pending_flag = _scan(committed)

    if subcommand is None:
        return list(SUBCOMMANDS)
    if subcommand == "configure":
        return _complete_configure(positionals)

    config = KubeConfig()
    active_scope = _active_scope(config)

    if subcommand == "switch":
        return _complete_switch(positionals, config)
    if subcommand == "list":
        return _complete_list(positionals, pending_flag, config, active_scope)
    if subcommand == "shell":
        return _complete_shell(positionals, config, active_scope)

    return []


def _scan(tokens: list[str]) -> tuple[str | None, list[str], dict, str | None]:
    """Positionally scan `tokens`, tolerating flags before or after positionals.

    Returns `(subcommand, positionals, flags, pending_flag)`. `pending_flag`
    is set to the name of a value-taking flag (e.g. `"namespace"`) when it is
    the last token, with no value following it yet.
    """
    subcommand: str | None = None
    positionals: list[str] = []
    flags: dict = {}
    pending_flag: str | None = None

    index = 0
    count = len(tokens)
    while index < count:
        token = tokens[index]
        if token == "--json":
            flags["json"] = True
            pending_flag = None
        elif token == "--namespace":
            if index + 1 < count:
                flags["namespace"] = tokens[index + 1]
                index += 1
                pending_flag = None
            else:
                pending_flag = "namespace"
        else:
            if subcommand is None:
                subcommand = token
            else:
                positionals.append(token)
            pending_flag = None
        index += 1

    return subcommand, positionals, flags, pending_flag


def _active_scope(config: KubeConfig) -> str | None:
    """Detect the active scope, degrading to `None` on any exception."""
    try:
        return scope.detect_active_scope(config.data.get("contexts", {}))
    except Exception:  # noqa: BLE001 - any failure degrades to static-only candidates
        return None


def _complete_switch(positionals: list[str], config: KubeConfig) -> list[str]:
    if positionals:
        return []
    return list(config.data.get("contexts", {}).keys())


def _complete_list(
    positionals: list[str],
    pending_flag: str | None,
    config: KubeConfig,
    active_scope: str | None,
) -> list[str]:
    if pending_flag == "namespace":
        return _namespace_aliases(config, active_scope)
    if not positionals:
        return list(LIST_TARGETS)
    if positionals == ["pods"]:
        return ["--namespace"]
    return []


def _complete_shell(
    positionals: list[str], config: KubeConfig, active_scope: str | None
) -> list[str]:
    if not positionals:
        return _namespace_aliases(config, active_scope)
    if len(positionals) == 1:
        namespace_alias = positionals[0]
        return _pod_aliases(config, active_scope, namespace_alias)
    return []


def _complete_configure(positionals: list[str]) -> list[str]:
    if positionals:
        return []
    return list(CONFIGURE_TARGETS)


def _namespace_aliases(config: KubeConfig, active_scope: str | None) -> list[str]:
    return list(config.data.get("namespaces", {}).get(active_scope, {}).keys())


def _pod_aliases(
    config: KubeConfig, active_scope: str | None, namespace_alias: str
) -> list[str]:
    scoped_pods = scope.active_scope_pods(config.data.get("pods", {}), active_scope)
    return [
        alias
        for alias, alias_config in scoped_pods.items()
        if alias_config.get("namespace") in (None, namespace_alias)
    ]
