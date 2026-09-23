"""auth.py — AWS credential pre-check for kube.

Standalone, reusable helpers that detect where AWS credentials come from and
verify they are usable before touching the cluster.

`detect_credential_source()` inspects the environment: when both
`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are exported, the AWS CLI
uses them and the configured profile is ignored.

`check_aws_credentials()` wraps `aws sts get-caller-identity` via
`subprocess.run`, adding `--profile <profile>` only when a profile is given
(passing `--profile` would make the AWS CLI ignore exported credentials). A
non-zero exit code is treated as invalid/missing credentials. Never raises —
callers (e.g. `executor.py`'s `_switch`) need to print a clear abort message
and stop cleanly rather than crash.
"""

from __future__ import annotations

import os
import subprocess  # nosec B404 - usage confined to fixed CLI binaries via binaries.resolve(), list-form args, no shell

from kube import binaries

ENV_ACCESS_KEY = "AWS_ACCESS_KEY_ID"
ENV_SECRET_KEY = "AWS_SECRET_ACCESS_KEY"


def _is_set(name: str) -> bool:
    """Return whether environment variable `name` is non-empty after stripping."""
    return bool(os.environ.get(name, "").strip())


def detect_credential_source() -> str:
    """Detect where AWS credentials come from.

    Returns `"env"` when both `AWS_ACCESS_KEY_ID` and
    `AWS_SECRET_ACCESS_KEY` are non-empty, `"partial"` when exactly one of
    them is, and `"profile"` when neither is set. `AWS_SESSION_TOKEN` is
    ignored for detection.
    """
    access_key = _is_set(ENV_ACCESS_KEY)
    secret_key = _is_set(ENV_SECRET_KEY)

    if access_key and secret_key:
        return "env"
    if access_key or secret_key:
        return "partial"
    return "profile"


def check_aws_credentials(profile: str | None) -> tuple[bool, str | None]:
    """Check whether AWS credentials are valid.

    Runs `aws sts get-caller-identity`, appending `--profile <profile>` only
    when `profile` is not `None` (so exported environment credentials are
    honoured), and returns a `(success, error)` tuple: `success` is `True`
    when the command exits zero, `False` otherwise, and `error` carries the
    captured stderr (or a generic message) on failure, `None` on success.
    """
    command = [binaries.resolve("aws"), "sts", "get-caller-identity"]
    if profile is not None:
        command += ["--profile", profile]

    result = subprocess.run(  # nosec B603, B607 - fixed binary, list-form args, no shell
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        return True, None

    error = result.stderr.strip() if result.stderr else "aws sts get-caller-identity failed"
    return False, error
