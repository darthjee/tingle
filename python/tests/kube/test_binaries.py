"""Unit tests for kube.binaries."""

from __future__ import annotations

from unittest.mock import patch

from kube.binaries import resolve


@patch("kube.binaries.shutil.which")
def test_resolve_found_returns_absolute_path(mock_which):
    mock_which.return_value = "/usr/local/bin/kubectl"

    assert resolve("kubectl") == "/usr/local/bin/kubectl"
    mock_which.assert_called_once_with("kubectl")


@patch("kube.binaries.shutil.which")
def test_resolve_not_found_falls_back_to_bare_name(mock_which):
    mock_which.return_value = None

    assert resolve("kubectl") == "kubectl"
