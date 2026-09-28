# Add GlobMatcher
Create `python/check_file_size/glob_matcher.py` with a `GlobMatcher` class that
turns `.gitignore`-style globs into compiled regexes.

- `GlobMatcher(patterns: list[str])` drops empty patterns and compiles each of
  the rest **once** in `__init__`, with `re.IGNORECASE`.
- `matches(rel_path: str) -> bool` returns `True` when any compiled pattern
  `fullmatch`es `rel_path`. It returns `False` when there are no patterns.
- The translation, done by a small tokenizer:
  - Anchoring: strip a trailing `/` and remember it (it becomes `/**`). If the
    remaining pattern has no `/`, prefix it with `**/`. Strip a leading `/`.
  - `**` as a whole segment: `**/` at the start or middle becomes
    `(?:.*/)?`. A trailing `/**` becomes `/.*`. A lone `**` becomes `.*`.
  - `**` inside a segment, and `*`, become `[^/]*`. `?` becomes `[^/]`.
  - `[...]`: find the closing `]`. `!` right after `[` negates the class. The
    class never matches `/`, so emit something like `(?!/)[...]` or add `/`
    to a negated set. An unclosed `[` is a literal `\[`.
  - `\c` becomes `re.escape(c)`. Every other literal goes through `re.escape`.
- Keep methods small (Codacy limits cyclomatic complexity to 10), and write
  D212-style docstrings (summary on the first line), matching the module's
  neighbours.

Tests in the new `python/tests/check_file_size/test_glob_matcher.py`
(parametrised where possible) must cover:
- every token in the syntax table;
- anchored vs unanchored patterns (`*.py` vs `*/a.py`, and `src/*.py` not
  matching `lib/src/a.py`);
- a leading `/` and a trailing `/` (`fixtures/`, `src/gen/`);
- `**` at the start, in the middle (`a/**/b` matches `a/b`, `a/x/b` and
  `a/x/y/b`), at the end, and alone;
- `**` inside a segment;
- character classes, including `[!...]` and an unclosed `[`;
- escapes;
- case-insensitivity;
- full match (not a prefix or substring);
- dot-files (`*` matches `.env`);
- an empty pattern and an empty list.

## Files to Change
- `python/check_file_size/glob_matcher.py` — new module with the `GlobMatcher` class.
- `python/tests/check_file_size/test_glob_matcher.py` — new unit tests.
