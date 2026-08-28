"""constants.py — Config schema and defaults for kube.

Defines the `~/.tingle/kube/config.json` schema shape and its default
values. Data/constants only — no file I/O here (see `config.py`).
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar


class Constants:
    """Schema, defaults, and path constants for kube's config file."""

    # Where the config file lives
    CONFIG_PATH: ClassVar[Path] = Path.home() / ".tingle" / "kube" / "config.json"

    # Defaults applied when a top-level key is absent
    DEFAULT_AWS_PROFILE = "default"
    DEFAULT_POD_ID_PATTERN = r"^[a-z0-9]{10}$"
    DEFAULT_SHELL = "bash"

    DEFAULTS: ClassVar[dict[str, str]] = {
        "aws_profile": DEFAULT_AWS_PROFILE,
        "pod_id_pattern": DEFAULT_POD_ID_PATTERN,
        "shell": DEFAULT_SHELL,
    }

    # Top-level keys that must be present in the config file
    REQUIRED_KEYS: ClassVar[frozenset[str]] = frozenset({"version"})

    # Top-level keys that have defaults when absent
    DEFAULTED_KEYS: ClassVar[frozenset[str]] = frozenset(DEFAULTS.keys())

    # Top-level keys holding alias objects (context alias -> value),
    # optional and default to an empty object when absent
    OBJECT_KEYS: ClassVar[frozenset[str]] = frozenset({"contexts", "namespaces", "pods"})

    # All recognized top-level keys
    ALL_KEYS: ClassVar[frozenset[str]] = REQUIRED_KEYS | DEFAULTED_KEYS | OBJECT_KEYS

    # `pods` entries: {"prefix": <required>, "id_pattern": <optional>, "namespace": <optional>}
    POD_REQUIRED_FIELDS: ClassVar[frozenset[str]] = frozenset({"prefix"})
    POD_OPTIONAL_FIELDS: ClassVar[frozenset[str]] = frozenset({"id_pattern", "namespace"})
