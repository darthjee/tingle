# Spec: `--ignore` / `--include` globs

Sub-issue: #249. Shared contracts: [README.md](README.md) (flags, precedence,
filter order, exit codes).

## Behaviour

- `--ignore GLOB` (repeatable): drops every file whose path matches any
  `--ignore` glob.
- `--include GLOB` (repeatable): when at least one is given, keeps only files
  whose path matches at least one `--include` glob. An empty `--include` list
  means include everything.
- Globs are matched against the file's **POSIX path relative to `<path>`**
  (e.g. `src/app/main.py` for `<path>` = the repo root). When `<path>` is a
  single file, globs are matched against its **file name**.
- Matching is **case-insensitive**, like `--exclude` and `--ext`.
- Glob syntax:

  | Token | Meaning |
  |-------|---------|
  | `*` | Any run of characters except `/` (may be empty). |
  | `?` | Exactly one character except `/`. |
  | `[abc]`, `[a-z]`, `[!abc]` | One character from (or, with `!`, not from) the set. Never matches `/`. An unclosed `[` is a literal `[`. |
  | `**` as a whole segment | Zero or more directories: `**/x`, `a/**`, `a/**/b`. A lone `**` matches everything. |
  | `**` inside a segment (`a**b`) | Same as `*`. |
  | `\c` | The literal character `c`. |

- Anchoring, as in `.gitignore`:
  - A pattern with **no `/`** (ignoring a trailing one) matches in any
    directory: `*.test.js` is the same as `**/*.test.js`.
  - A pattern **with a `/`** is anchored at `<path>`: `src/*.py` matches
    `src/a.py` but not `lib/src/a.py`. A leading `/` is allowed and only
    marks the anchor (`/src/*.py` is the same as `src/*.py`).
  - A **trailing `/`** matches everything under that directory: `fixtures/`
    is the same as `**/fixtures/**`, and `src/gen/` is the same as
    `src/gen/**`.
- The whole path must match (full match, not a prefix or substring).
- Order in the pipeline (see README section 5): after `.gitignore`, before the
  `--ext` and binary checks. `--ignore` therefore wins over `--include`.
- `--include` and `--ext` are combined with AND: when both are given, a file
  must match an include glob **and** have a listed extension.

## Examples

| Invocation | Effect |
|------------|--------|
| `tingle check_file_size . --ignore '*.test.js'` | Skips `a.test.js` and `src/b.TEST.js`. |
| `tingle check_file_size . --ignore 'docs/**' --ignore '*.md'` | Skips everything under `docs/` and every Markdown file. |
| `tingle check_file_size . --include 'src/**'` | Analyses only files under `src/`. |
| `tingle check_file_size . --include 'src/**' --ext .py` | Only `.py` files under `src/`. |
| `tingle check_file_size . --include 'src/**' --ignore 'src/vendor/'` | Files under `src/`, except `src/vendor/`. |
| `tingle check_file_size ./main.py --ignore 'main.*'` | Nothing to analyse, so it prints "No files found for analysis." and exits 0. |

## Edge cases

- An empty pattern (`--ignore ''`) is dropped and matches nothing.
- A glob that matches nothing is not an error.
- `*.py` matches `a.py` and `x/y/a.py` (unanchored), but `*/a.py` matches only
  `x/a.py` (anchored, and `*` does not cross `/`).
- `a/**/b` matches `a/b`, `a/x/b` and `a/x/y/b`.
- Dot-files get no special treatment: `*` matches `.env`.
- Paths use `/` on every platform (`PurePath.as_posix()`).

## Technical decisions

- Python 3.11 has no `PurePath.full_match`, and `fnmatch` lets `*` cross `/`.
  So a new module `python/check_file_size/glob_matcher.py` translates globs to
  regexes itself:
  - `GlobMatcher(patterns: list[str])` compiles each pattern **once** in
    `__init__`, with `re.IGNORECASE`, using the rules above. Empty patterns
    are dropped.
  - `GlobMatcher.matches(rel_path: str) -> bool` returns `True` when any
    compiled pattern `fullmatch`es `rel_path`. With no patterns, it returns
    `False`.
  - The translation is a small tokenizer (no `fnmatch.translate`). Literal
    characters go through `re.escape`.
- `FileCollector` gains two constructor arguments, `ignore: list[str]` and
  `include: list[str]`, and builds one `GlobMatcher` for each. It computes the
  relative POSIX path once per file (`path.relative_to(target).as_posix()`, or
  `target.name` for a single file) and passes it to both matchers.
- `executor.py` adds `--ignore` and `--include` to `FLAGS` with
  `action: "append"` and `default: None`, treating `None` as `[]`.

## Tests expected

- `python/tests/check_file_size/test_glob_matcher.py` (new): every token in
  the syntax table, anchored vs unanchored patterns, leading and trailing `/`,
  `**` at the start, middle, end and alone, `**` inside a segment, character
  classes including `[!...]` and an unclosed `[`, escapes, case-insensitivity,
  full match, empty pattern and empty list.
- `test_file_collector.py`: `--ignore` drops matches; `--include` keeps only
  matches; `--include` + `--ext` is an AND; `--ignore` wins over `--include`;
  a single-file `<path>` matches on its name.
- `test_executor.py`: both flags parse as repeatable lists and reach the
  collector.
