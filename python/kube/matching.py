"""
matching.py — Pod-matching pipeline for kube discovery.

Standalone, reusable filter/sort pipeline: given a flat list of pods (as
returned by `kube/inventory.py`) and a pod alias's `prefix` + `id_pattern`
config, returns the pods whose name matches the alias's rule, ordered
deterministically by creation time (oldest first). Reused by `shell`'s
collapse-to-one-target logic rather than being re-implemented there.
"""

from __future__ import annotations

import re


def match_pods(
    pods: list[dict], prefix: str, id_pattern: str | None, default_id_pattern: str
) -> list[dict]:
    """Filter and order `pods` matching `prefix` + `id_pattern`.

    Keeps pods whose name starts with `prefix` and whose remaining suffix
    (the part of the name after `prefix`) fully matches `id_pattern` (or
    `default_id_pattern` when `id_pattern` is falsy/`None`). Surviving pods
    are sorted by `creationTimestamp` ascending (oldest first) — a
    deterministic ordering, not a collapse to a single pod.
    """
    pattern = id_pattern or default_id_pattern
    compiled = re.compile(pattern)

    matched = []
    for pod in pods:
        name = pod["metadata"]["name"]
        if not name.startswith(prefix):
            continue

        suffix = name[len(prefix):]
        if compiled.fullmatch(suffix):
            matched.append(pod)

    return sorted(matched, key=lambda pod: pod["metadata"]["creationTimestamp"])
