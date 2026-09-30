"""Shared fixtures for check_file_size tests."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolate_home(monkeypatch, tmp_path_factory):
    """Keep tests hermetic: point HOME at an empty temp dir so no real config is read."""
    monkeypatch.setenv("HOME", str(tmp_path_factory.mktemp("home")))
