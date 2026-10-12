"""Unit tests for code_check.docker_check.image.resolve_image."""

from __future__ import annotations

import pytest

from code_check.docker_check.errors import DockerCheckError
from code_check.docker_check.image import resolve_image

REPO = "darthjee/tingle_other"


class OtherError(DockerCheckError):
    """A check-specific error class."""


def test_explicit_image_wins(tmp_path):
    image = resolve_image("other:dev", REPO, tmp_path / "missing", error_class=OtherError)

    assert image == "other:dev"


def test_default_image_uses_repo_and_trimmed_version(tmp_path):
    version = tmp_path / "VERSION"
    version.write_text("  1.2 .3 \n\n")

    assert resolve_image(None, REPO, version, error_class=OtherError) == f"{REPO}:1.2.3"


def test_empty_cli_image_falls_back_to_default(tmp_path):
    version = tmp_path / "VERSION"
    version.write_text("0.1.0\n")

    assert resolve_image("", REPO, version, error_class=OtherError) == f"{REPO}:0.1.0"


@pytest.mark.parametrize("content", [None, "", " \n\t", b"\xff\xfe"], ids=[
    "missing", "empty", "blank", "not-utf8",
])
def test_unreadable_version_raises_error_class(tmp_path, content):
    version = tmp_path / "VERSION"
    if isinstance(content, bytes):
        version.write_bytes(content)
    elif content is not None:
        version.write_text(content)

    with pytest.raises(OtherError) as exc_info:
        resolve_image(None, REPO, version, error_class=OtherError)

    assert exc_info.value.message == (
        f"cannot read the tingle version from {version}; use --image to choose the image"
    )


def test_directory_version_file_raises(tmp_path):
    with pytest.raises(OtherError):
        resolve_image(None, REPO, tmp_path, error_class=OtherError)
