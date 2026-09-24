# Plan: Codacy: Method _flags has 55 lines of code (limit is 50) (python/check_file_size/executor.py:46)

Issue: [201-codacy-method-flags-has-55-lines-of-code-limit-is-50-python-check-file-size-executor-py-46.md](../../issues/201-codacy-method-flags-has-55-lines-of-code-limit-is-50-python-check-file-size-executor-py-46.md)

## Overview
Replace the `CheckFileSize._flags()` static method with a module-level
`FLAGS` constant in `python/check_file_size/executor.py`, so Lizard no
longer counts the flag list as a 55-line function. CLI behaviour is unchanged.

See [python.md](python.md) for the full plan.
