"""image.py — Resolve the Docker image that runs RubyCritic.

`--image` wins when given. Otherwise the image is
`darthjee/tingle_rubycritic:<version>`, where `<version>` is the content of
`shell/linux/VERSION` with all whitespace removed. The logic lives in
`code_check.docker_check.image`; this wrapper binds the RubyCritic values.
"""

from __future__ import annotations

from pathlib import Path

from code_check.docker_check import image as docker_check_image
from code_check.rubycritic.constants import Constants
from code_check.rubycritic.errors import RubycriticError


def resolve_image(cli_image: str | None, version_file: Path | None = None) -> str:
    """Return `cli_image`, or the default image tagged with the tingle version.

    `version_file` defaults to `Constants.VERSION_FILE` (read at call time).
    Raises `RubycriticError` when the version file is missing, unreadable or
    empty (and no image was given).
    """
    if version_file is None:
        version_file = Constants.VERSION_FILE
    return docker_check_image.resolve_image(
        cli_image, Constants.IMAGE_REPO, version_file, error_class=RubycriticError
    )
