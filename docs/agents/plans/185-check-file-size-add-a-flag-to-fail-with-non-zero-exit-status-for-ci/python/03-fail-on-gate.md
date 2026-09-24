# Add the --fail-on gate
- Add a flag to `CheckFileSize._flags()`:
  `{"name": "--fail-on", "type": str, "choices": ["warn", "error", "critical"], "default": None, "help": "Exit with status 2 if any file reaches this level or higher"}`.
  (`ArgParser` forwards extra keys to `add_argument`, so `choices` works.)
  Parsed key: `args["fail_on"]`.
- In `run`, after sorting and **before** the `--top` slice, work out whether
  any result breaches the gate. Use the thresholds (`lines >= warn/error/critical`
  for the selected level), or add a helper on `FileAnalyzer` such as
  `level_rank(lines)` / `reaches(lines, level)` rather than string-matching
  labels.
- Print the report as today, then `sys.exit(2)` if the gate failed.
  Otherwise return normally (exit 0).
- The "No files found" path keeps exiting 0.

Tests: for each level, a fixture that passes and one that fails (exit 2).
A file hidden by `--top 1` still fails the gate. No `--fail-on` means no
non-zero exit even with CRITICAL files. `--fail-on foo` exits 1 (via step 02).
An empty directory with `--fail-on warn` exits 0. The report is still printed
when the gate fails.

## Files to Change
- `python/check_file_size/executor.py`: new flag and gate evaluation before `--top`
- `python/check_file_size/file_analyzer.py`: optional level-comparison helper
- `python/tests/check_file_size/test_executor.py`: gate tests
- `python/tests/check_file_size/test_file_analyzer.py`: helper tests, if added
