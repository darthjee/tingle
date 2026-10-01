# Docker runner

Create `python/code_check/rubycritic/docker_runner.py` with `class DockerRunner(image)`. It calls `shutil.which` and `subprocess.run` through module-level imports so tests can patch them. Every failure raises `RubycriticError`, with messages verbatim from spec §10.

**`preflight()`**
- `shutil.which("docker")` must find docker, or it fails with `docker not found on PATH`.
- Then run `docker info` with stdout and stderr sent to DEVNULL and `timeout=Constants.DOCKER_INFO_TIMEOUT`.
- A non-zero exit, `TimeoutExpired` or `OSError` means the daemon is not responding.

**`ensure_image()`**
- Run `docker image inspect <image>` quietly.
- If that fails, print `Pulling <image> ...` and run `docker pull <image>` with its output sent to stderr. Flush first, and fall back if `fileno()` is unavailable.
- A failed pull is an error.

**`run(root, lines) -> CompletedProcess`**
- The exact argv is:
  ```
  docker run --rm -i --pull never --network none --security-opt no-new-privileges --user <os.getuid()>:<os.getgid()> -v <root>:/src:ro -w /src <image>
  ```
- Pass `input="\n".join(lines) + "\n"` as UTF-8 bytes, with `capture_output=True` and no timeout.

**`check_outcome(proc)`**
- Exit 125 with any `MOUNT_ERROR_MARKERS` in stderr → the Docker Desktop file-sharing hint.
- Any other non-zero exit → write the container stderr through to our stderr, then fail with `RubycriticError("RubyCritic failed in <image> (exit N)")`.
- Decode output with `errors="replace"`.

Wire into the executor in this order: preflight, then ensure_image, then run, then check_outcome. All of them are caught by the single `RubycriticError` handler.

Tests cover:
- the exact argv and stdin bytes;
- `which` missing;
- `docker info` failing, timing out and raising `OSError`;
- inspect succeeding, so no pull;
- inspect failing, then the pull succeeding or failing;
- exit 125 with each marker;
- exit 125 without a marker;
- other non-zero exits, with stderr passed through.

## Files to Change
- `python/code_check/rubycritic/docker_runner.py`: new.
- `python/code_check/rubycritic/executor.py`: call the runner steps.
- `python/tests/code_check/rubycritic/test_docker_runner.py`: new.
