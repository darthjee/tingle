"""
config.py — Load, validate, and default ~/.tingle/kube/config.json.

Reads the config file, validates its shape against the schema in
`constants.py`, and applies defaults for `aws_profile`, `pod_id_pattern`,
and `shell` when absent. A missing file, invalid JSON, or a structurally
invalid config does not raise — it flags "pass-through mode" instead,
exposing a notice message for the caller (`executor.py`) to print.
"""

from __future__ import annotations

import json
from pathlib import Path

from kube.constants import Constants


class KubeConfig:
    """Load ~/.tingle/kube/config.json, validating and defaulting it."""

    def __init__(self, path: Path | None = None):
        self._path = path or Constants.CONFIG_PATH
        self.pass_through = False
        self.notice: str | None = None
        self.data: dict = {}
        self._load()

    def _load(self) -> None:
        raw = self._read()
        if raw is None:
            return

        error = self._validate(raw)
        if error:
            self._fallback(error)
            return

        self.data = self._apply_defaults(raw)

    def _read(self) -> dict | None:
        """Read and JSON-parse the config file, flagging pass-through on failure."""
        if not self._path.exists():
            self._fallback(f"config not found at {self._path}")
            return None

        try:
            text = self._path.read_text()
        except OSError as exc:
            self._fallback(f"could not read config at {self._path}: {exc}")
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            self._fallback(f"invalid JSON in config at {self._path}: {exc}")
            return None

    def _validate(self, raw: object) -> str | None:
        """Validate the parsed config's shape. Returns an error message, if any."""
        if not isinstance(raw, dict):
            return "config must be a JSON object"

        missing = Constants.REQUIRED_KEYS - raw.keys()
        if missing:
            return f"config missing required key(s): {', '.join(sorted(missing))}"

        for key in Constants.OBJECT_KEYS:
            if key in raw and not isinstance(raw[key], dict):
                return f"config key '{key}' must be an object"

        return self._validate_pods(raw.get("pods", {}))

    def _validate_pods(self, pods: object) -> str | None:
        """Validate the (optional) two-level `pods` structure."""
        if not isinstance(pods, dict):
            return None

        for context_alias, entries in pods.items():
            if not isinstance(entries, dict):
                return f"config pods.{context_alias} must be an object"
            for pod_alias, pod in entries.items():
                if not isinstance(pod, dict):
                    return f"config pods.{context_alias}.{pod_alias} must be an object"
                missing_fields = Constants.POD_REQUIRED_FIELDS - pod.keys()
                if missing_fields:
                    return (
                        f"config pods.{context_alias}.{pod_alias} missing required "
                        f"field(s): {', '.join(sorted(missing_fields))}"
                    )

        return None

    @staticmethod
    def _apply_defaults(raw: dict) -> dict:
        """Return a copy of `raw` with defaults applied for absent keys."""
        data = dict(raw)
        for key, default in Constants.DEFAULTS.items():
            data.setdefault(key, default)
        for key in Constants.OBJECT_KEYS:
            data.setdefault(key, {})
        return data

    def _fallback(self, reason: str) -> None:
        """Flag pass-through mode with a human-readable notice."""
        self.pass_through = True
        self.notice = f"kube: {reason} — falling back to pass-through mode."
