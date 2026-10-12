"""image.py — Resolve the Docker image that runs a check's tool.

`--image` wins when given. Otherwise the image is `<repo>:<version>`, where
`<version>` is the content of the version file with all whitespace removed.
"""

from __future__ import annotations

from pathlib import Path

from code_check.docker_check.errors import DockerCheckError


def resolve_image(
    cli_image: str | None,
    repo: str,
    version_file: Path,
    *,
    error_class: type[DockerCheckError],
) -> str:
    """Return `cli_image`, or the `repo` image tagged with the tingle version.

    `version_file` is passed by the caller at call time. Raises `error_class`
    when the version file is missing, unreadable or empty (and no image was
    given).
    """
    if cli_image:
        return cli_image
    try:
        version = "".join(version_file.read_text(encoding="utf-8").split())
    except (OSError, UnicodeDecodeError):
        version = ""
    if not version:
        raise error_class(
            f"cannot read the tingle version from {version_file}; "
            "use --image to choose the image"
        )
    return f"{repo}:{version}"
