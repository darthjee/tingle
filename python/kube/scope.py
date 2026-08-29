"""
scope.py — Context alias resolution and active-scope detection for kube.

Standalone, reusable functions wrapping `kubectx`/`kubectl` subprocess calls:
resolving a `context_alias` against the config's `contexts` dict, switching
and validating the result, listing the available contexts (for error-path
suggestions), and detecting which alias (if any) is currently active. None
of these raise — callers print their own messages and decide how to proceed.
"""

from __future__ import annotations

import subprocess


def resolve_context_alias(contexts: dict, context_alias: str) -> tuple[str, str | None]:
    """Resolve `context_alias` against `contexts` (alias -> real name/ARN).

    Returns a `(real_name, notice)` tuple. When the alias is found, `notice`
    is `None`. When it isn't, the literal `context_alias` is passed through
    unchanged as `real_name`, alongside a caller-visible notice.
    """
    if context_alias in contexts:
        return contexts[context_alias], None

    notice = f"kube: '{context_alias}' not found in configured contexts — using it as-is."
    return context_alias, notice


def switch_context(real_name: str) -> tuple[bool, str | None]:
    """Switch to `real_name` via `kubectx` and validate via `kubectl`.

    Returns a `(success, error)` tuple. `error` carries the captured stderr
    (or a mismatch message) on failure, `None` on success.
    """
    result = subprocess.run(
        ["kubectx", real_name],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        error = result.stderr.strip() if result.stderr else f"kubectx {real_name} failed"
        return False, error

    current = subprocess.run(
        ["kubectl", "config", "current-context"],
        capture_output=True,
        text=True,
        check=False,
    )
    if current.returncode != 0:
        error = (
            current.stderr.strip()
            if current.stderr
            else "kubectl config current-context failed"
        )
        return False, error

    current_context = current.stdout.strip()
    if current_context != real_name:
        return False, f"expected current context '{real_name}', got '{current_context}'"

    return True, None


def list_available_contexts(contexts: dict) -> list[str]:
    """List the available context aliases, for error-path suggestions.

    Prefers the config's own `contexts` keys when present; falls back to
    parsing `kubectl config get-contexts -o name` when config has none
    (pass-through mode).
    """
    if contexts:
        return sorted(contexts.keys())

    result = subprocess.run(
        ["kubectl", "config", "get-contexts", "-o", "name"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def detect_active_scope(contexts: dict) -> str | None:
    """Detect the currently active context's alias, if any.

    Runs `kubectl config current-context` and reverse-looks-up the result in
    `contexts` (value -> key). Returns the matching alias, or `None` when
    the current context isn't in `contexts` (no scope / pass-through mode).
    """
    result = subprocess.run(
        ["kubectl", "config", "current-context"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    current_context = result.stdout.strip()
    reverse = {real_name: alias for alias, real_name in contexts.items()}
    return reverse.get(current_context)
