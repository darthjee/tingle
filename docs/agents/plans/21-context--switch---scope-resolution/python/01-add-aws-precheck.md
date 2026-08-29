# Add the AWS pre-check module

Add a standalone, reusable AWS credential pre-check that `_switch` (and, later, children #22/#23) can call before touching the cluster. Run `aws sts get-caller-identity --profile <aws_profile>` via `subprocess.run`; treat a non-zero exit code as invalid credentials. Return a simple pass/fail signal plus the captured stderr so the caller can print a clear abort message — don't raise, since `_switch` needs to print a message and stop cleanly rather than crash.

## Files to Change

- `python/kube/auth.py` (new) — a single function, e.g. `check_aws_credentials(profile: str) -> tuple[bool, str | None]`, wrapping the `aws sts get-caller-identity --profile <profile>` subprocess call.
- `python/tests/kube/test_auth.py` (new) — unit tests covering: success (mocked zero exit code), failure (mocked non-zero exit code + stderr surfaced), and that the correct `--profile` value is passed through. Mock `subprocess.run` rather than shelling out to a real `aws` binary.
