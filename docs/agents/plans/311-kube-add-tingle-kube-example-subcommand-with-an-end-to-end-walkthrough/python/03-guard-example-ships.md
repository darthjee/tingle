# Guard that the example ships

Make sure a later change to the release allowlist cannot silently drop the
example file.

- `python/tests/kube/test_example.py`: add a test that reads
  `scripts/release_cli.sh` (resolved from the repo root, i.e.
  `Path(__file__).resolve().parents[3] / "scripts" / "release_cli.sh"`),
  extracts the `INCLUDES="..."` value, and asserts that the first path
  component of `EXAMPLE_PATH` relative to the repo root (`examples`) is one
  of its tokens, and that it does not match `PRUNE_PATTERN`.

## Files to Change

- `python/tests/kube/test_example.py` — release-allowlist guard.
