"""
inventory.py — Kubectl inventory helpers for kube.

Standalone, reusable functions wrapping the read-only `kubectl` calls needed
for discovery: listing namespaces and listing pods within a namespace. Dumb
wrappers only — no alias resolution or filtering here (see `scope.py` and
`matching.py`). Never raise — callers print their own messages and decide
how to proceed.
"""

from __future__ import annotations

import json
import subprocess


def list_namespaces() -> tuple[list[dict], str | None]:
    """List all namespaces via `kubectl get namespaces -o json`.

    Returns an `(items, error)` tuple: `items` is the parsed `"items"` list
    (each a raw namespace dict) and `error` is `None` on success, or `([],
    error)` on a non-zero exit or JSON parse failure.
    """
    result = subprocess.run(
        ["kubectl", "get", "namespaces", "-o", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        error = result.stderr.strip() if result.stderr else "kubectl get namespaces failed"
        return [], error

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return [], f"failed to parse kubectl output: {exc}"

    return data.get("items", []), None


def list_pods(namespace: str) -> tuple[list[dict], str | None]:
    """List all pods in `namespace` via `kubectl get pods -n <namespace> -o json`.

    Returns an `(items, error)` tuple: `items` is the parsed `"items"` list
    (each a raw pod dict) and `error` is `None` on success, or `([], error)`
    on a non-zero exit (e.g. nonexistent namespace) or JSON parse failure.
    """
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        error = result.stderr.strip() if result.stderr else "kubectl get pods failed"
        return [], error

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return [], f"failed to parse kubectl output: {exc}"

    return data.get("items", []), None
