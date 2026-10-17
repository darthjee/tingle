"""image.py — Resolve the Docker image that runs PDepend.

`--image` wins when given. Otherwise the image is
`darthjee/tingle_php_complexity:<version>`, where `<version>` is the content
of `shell/linux/VERSION` with all whitespace removed. The logic lives in
`code_check.docker_check.image`; this wrapper binds the php_complexity values.
"""

from __future__ import annotations

from pathlib import Path

from code_check.docker_check import image as docker_check_image
from code_check.php_complexity.constants import Constants
from code_check.php_complexity.errors import PhpComplexityError


def resolve_image(cli_image: str | None, version_file: Path | None = None) -> str:
    """Return `cli_image`, or the default image tagged with the tingle version.

    `version_file` defaults to `Constants.VERSION_FILE` (read at call time).
    Raises `PhpComplexityError` when the version file is missing, unreadable
    or empty (and no image was given).
    """
    if version_file is None:
        version_file = Constants.VERSION_FILE
    return docker_check_image.resolve_image(
        cli_image, Constants.IMAGE_REPO, version_file, error_class=PhpComplexityError
    )
