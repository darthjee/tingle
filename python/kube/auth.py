"""
auth.py — AWS credential pre-check for kube.

Standalone, reusable helper that verifies AWS credentials are usable for a
given profile before touching the cluster. Wraps
`aws sts get-caller-identity --profile <profile>` via `subprocess.run`; a
non-zero exit code is treated as invalid/missing credentials. Never raises —
callers (e.g. `executor.py`'s `_switch`) need to print a clear abort message
and stop cleanly rather than crash.
"""

from __future__ import annotations

import subprocess


def check_aws_credentials(profile: str) -> tuple[bool, str | None]:
    """Check whether AWS credentials for `profile` are valid.

    Runs `aws sts get-caller-identity --profile <profile>` and returns a
    `(success, error)` tuple: `success` is `True` when the command exits
    zero, `False` otherwise, and `error` carries the captured stderr (or a
    generic message) on failure, `None` on success.
    """
    result = subprocess.run(
        ["aws", "sts", "get-caller-identity", "--profile", profile],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        return True, None

    error = result.stderr.strip() if result.stderr else "aws sts get-caller-identity failed"
    return False, error
