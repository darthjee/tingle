# Plan: Codacy: File has 563 non-comment lines of code (python/tests/kube/test_executor.py:1)

Issue: [73-codacy-file-has-563-non-comment-lines-of-code-python-tests-kube-test-executor-py-1.md](../../issues/73-codacy-file-has-563-non-comment-lines-of-code-python-tests-kube-test-executor-py-1.md)

## Overview

Split `python/tests/kube/test_executor.py` (683 lines, 28 tests covering every
static method on `kube.executor.Kube`) into five smaller files, one per
method under test, so no single file exceeds Codacy's `Lizard_file-nloc-medium`
threshold or this repo's own `check_file_size` limits. Purely a test
reorganization — no test bodies or assertions change.

See [python.md](python.md) for the full plan.
