# File selection

Create `python/code_check/rubycritic/selection.py` with a `Selection` dataclass (`root: Path`, `lines: list[str]`, `skipped: list[str]`) and a function or class that builds it from the resolved target.

**Mount root**
- For a directory, the root is the directory itself.
- For a single file, the root is its parent directory, and only the file name is sent.

**Collecting files**
- Call `FileCollector(Constants.DEFAULT_EXCLUDES, Constants.EXTENSIONS, gitignore=False, binary_check=False)`.
- The `.rb` match is case-insensitive.
- Excludes are not applied to a single-file target, matching `file_size`.

**Lines sent to the container**
- Convert each file to a POSIX path relative to the root.
- Sort the lines.

**Unsendable names** (spec §8.5)
- A name is unsendable if it contains `"\n"`, or if `rel.encode("utf-8")` raises `UnicodeEncodeError` (a surrogate escape).
- Unsendable names are skipped with `Warning: …` on stderr and are not counted.

In the executor, after the header:
- If no lines remain, print `No Ruby files found for analysis.` and exit 0.
- Make no Docker call in that case, not even the preflight.

Tests:
- directory mode: sorted relative lines, the extra excludes (`tmp`, `log`, `.bundle`), and an uppercase `.RB` file;
- single-file mode: the root is the parent and only the name is sent;
- a non-`.rb` single file;
- newline and surrogate names, built as synthetic strings;
- the no-files path, asserting that `which` and `run` are never called.

## Files to Change
- `python/code_check/rubycritic/selection.py`: new.
- `python/code_check/rubycritic/executor.py`: wire selection and the "No Ruby files found" exit.
- `python/tests/code_check/rubycritic/test_selection.py`: new.
- `python/tests/code_check/rubycritic/test_executor.py`: no-files case.
