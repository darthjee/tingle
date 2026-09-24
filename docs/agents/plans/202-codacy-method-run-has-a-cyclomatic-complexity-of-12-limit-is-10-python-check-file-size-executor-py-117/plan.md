# Plan: Codacy: Method run has a cyclomatic complexity of 12 (limit is 10) (python/check_file_size/executor.py:117)

Issue: [202-codacy-method-run-has-a-cyclomatic-complexity-of-12-limit-is-10-python-check-file-size-executor-py-117.md](../../issues/202-codacy-method-run-has-a-cyclomatic-complexity-of-12-limit-is-10-python-check-file-size-executor-py-117.md)

## Overview
Behaviour-preserving refactor of `CheckFileSize.run()` in `python/check_file_size/executor.py`: extract cohesive steps into private helpers so `run()` drops from cyclomatic complexity 12 to well under 10. Owned entirely by the `python` agent.

See [python.md](python.md) for the full plan.
