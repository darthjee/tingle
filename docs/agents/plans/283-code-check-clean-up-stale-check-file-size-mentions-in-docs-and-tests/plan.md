# Plan: code_check: clean up stale check_file_size mentions in docs and tests

Issue: [283-code-check-clean-up-stale-check-file-size-mentions-in-docs-and-tests.md](../../issues/283-code-check-clean-up-stale-check-file-size-mentions-in-docs-and-tests.md)

## Overview

This is the last cleanup for #279. `docs/agents/architecture.md` still describes
the `check_file_size` shim as it was before #281. It needs to say that the shim
prints a deprecation warning. Two tests in `python/tests/code_check/` still use
the old name: one uses it as a section name, the other in a test name. The
`CheckFileSize` class name stays as it is.

## Agents involved

- [product-owner](product-owner.md)
- [python](python.md)

## Shared contracts

None. The docs change and the test change are independent. Both follow the same
rule: after this issue, `check_file_size` only refers to one of these:

- the deprecated alias (`python/check_file_size/`, its `commands/python.json`
  entry, its tests and `docs/guides/check_file_size.md`);
- the legacy config key (`LEGACY_CONFIG_SECTION` in
  `python/code_check/file_size/executor.py`, its tests and docs);
- the migration notes in `docs/guides/code_check.md` and
  `docs/guides/code_check/file_size.md`.
