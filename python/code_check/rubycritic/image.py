"""image.py — Resolve the Docker image that runs RubyCritic.

`--image` wins when given. Otherwise the image is
`darthjee/tingle_rubycritic:<version>`, where `<version>` is the content of
`shell/linux/VERSION` with all whitespace removed.
"""

from __future__ import annotations

from pathlib import Path

from code_check.rubycritic.constants import Constants
from code_check.rubycritic.errors import RubycriticError


def resolve_image(cli_image: str | None, version_file: Path | None = None) -> str:
    """Return `cli_image`, or the default image tagged with the tingle version.

    `version_file` defaults to `Constants.VERSION_FILE` (read at call time).
    Raises `RubycriticError` when the version file is missing, unreadable or
    empty (and no image was given).
    """
    if cli_image:
        return cli_image
    if version_file is None:
        version_file = Constants.VERSION_FILE
    try:
        version = "".join(version_file.read_text(encoding="utf-8").split())
    except (OSError, UnicodeDecodeError):
        version = ""
    if not version:
        raise RubycriticError(
            f"cannot read the tingle version from {version_file}; "
            "use --image to choose the image"
        )
    return f"{Constants.IMAGE_REPO}:{version}"
