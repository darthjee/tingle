"""Shared fixtures for kube tests."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clear_aws_env_credentials(monkeypatch):
    """Keep tests hermetic: drop any AWS credentials exported in the host environment."""
    for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
        monkeypatch.delenv(name, raising=False)
