# Plan: check_file_size: add --ignore and --include glob flags

Issue: [249-check-file-size-add-ignore-and-include-glob-flags.md](../../issues/249-check-file-size-add-ignore-and-include-glob-flags.md)

## Overview
Add two repeatable glob flags to `tingle check_file_size`: `--ignore` drops
matching files, and `--include` keeps only matching files. The python agent
adds a `GlobMatcher` (a glob-to-regex translator), wires it into
`FileCollector` and `executor.py`, and adds tests. The cli agent documents the
flags in `long_help`, and the guide agent documents them in the user guide.
The full contract is in
[`docs/agents/specs/check_file_size/ignore-include.md`](../../specs/check_file_size/ignore-include.md)
and the shared [README.md](../../specs/check_file_size/README.md). If this plan
and the specs disagree, the specs win.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

- Flags: `--ignore GLOB` and `--include GLOB`, both repeatable
  (`action: "append"`, `default: None`, with `None` treated as `[]`).
- Globs are matched against the file's POSIX path relative to `<path>`, or
  against the file name when `<path>` is a single file. Matching is a
  case-insensitive **full match**.
- Syntax: `*` and `?` never cross `/`; `[abc]`, `[a-z]` and `[!abc]` never
  match `/`, and an unclosed `[` is a literal; `**` as a whole segment means
  zero or more directories (inside a segment it acts like `*`); `\c` is a
  literal `c`.
- Anchoring, as in `.gitignore`: a pattern with no `/` matches in any
  directory; a pattern with a `/` is anchored at `<path>` (a leading `/` only
  marks the anchor); a trailing `/` matches everything under that directory.
- `--ignore` wins over `--include`. `--include` and `--ext` are combined with
  AND. With no `--include`, everything is included.
- Empty patterns are dropped. A glob that matches nothing is not an error. When
  every file is filtered out, the tool prints "No files found for analysis."
  and exits 0.
- Filter order in `FileCollector`: excludes → (`.gitignore`, #251) →
  `--ignore` → `--include`/`--ext` → binary check.
- Canonical examples, to be used the same way in `long_help` and in the guide:
  - `--ignore '*.test.js'`
  - `--ignore 'docs/**' --ignore '*.md'`
  - `--include 'src/**'`
  - `--include 'src/**' --ext .py`
  - `--include 'src/**' --ignore 'src/vendor/'`
- Help text in `FLAGS`:
  - `--ignore`: "Skip files whose path relative to <path> matches this glob (can be repeated)"
  - `--include`: "Only analyse files whose path relative to <path> matches this glob (can be repeated)"
