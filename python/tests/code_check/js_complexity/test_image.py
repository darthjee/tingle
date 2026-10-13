"""Unit tests for code_check.js_complexity.image.resolve_image."""

from __future__ import annotations

import pytest

from code_check.js_complexity.constants import Constants
from code_check.js_complexity.errors import JsComplexityError
from code_check.js_complexity.image import resolve_image


def test_explicit_image_wins(tmp_path):
    assert (
        resolve_image("tingle_js_complexity:dev", tmp_path / "missing")
        == "tingle_js_complexity:dev"
    )


def test_default_image_uses_trimmed_version(tmp_path):
    version = tmp_path / "VERSION"
    version.write_text("  0.9.0 \n\n")

    assert resolve_image(None, version) == "darthjee/tingle_js_complexity:0.9.0"


def test_default_image_removes_inner_whitespace(tmp_path):
    version = tmp_path / "VERSION"
    version.write_text("0.9\n.0\n")

    assert resolve_image(None, version) == "darthjee/tingle_js_complexity:0.9.0"


def test_missing_version_file_raises(tmp_path):
    missing = tmp_path / "VERSION"

    with pytest.raises(JsComplexityError) as exc_info:
        resolve_image(None, missing)

    assert exc_info.value.message == (
        f"cannot read the tingle version from {missing}; use --image to choose the image"
    )


def test_empty_version_file_raises(tmp_path):
    version = tmp_path / "VERSION"
    version.write_text(" \n\t\n")

    with pytest.raises(JsComplexityError, match="cannot read the tingle version"):
        resolve_image(None, version)


def test_version_file_points_at_repo_shell_linux_version():
    assert Constants.VERSION_FILE.parts[-3:] == ("shell", "linux", "VERSION")


def test_version_file_defaults_to_constant_at_call_time(tmp_path, monkeypatch):
    version = tmp_path / "VERSION"
    version.write_text("1.2.3\n")
    monkeypatch.setattr(Constants, "VERSION_FILE", version)

    assert resolve_image(None) == "darthjee/tingle_js_complexity:1.2.3"
