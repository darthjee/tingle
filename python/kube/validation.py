"""validation.py — Kubernetes resource name validation for kube.

Validates caller-supplied resource names (namespaces, pod names, etc.)
against RFC 1123 label rules before they are interpolated into `kubectl`
argument lists in `inventory.py`, so that Bandit's "subprocess call - check
for execution of untrusted input" (B603) finding has an actual guard behind
it rather than relying solely on the list-form/no-shell invocation.
"""

from __future__ import annotations

import re

_RFC1123_LABEL_RE = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")


def is_valid_resource_name(value: str, *, max_length: int = 253) -> bool:
    """Return whether `value` is a valid RFC 1123 Kubernetes resource name.

    Valid names are lowercase alphanumeric characters and `-` only, must
    start and end with an alphanumeric character, and must not exceed
    `max_length` characters. Namespaces are capped at 63 chars by
    Kubernetes; other resource names (e.g. pod names) default to 253.
    """
    if not value or len(value) > max_length:
        return False

    return bool(_RFC1123_LABEL_RE.match(value))
