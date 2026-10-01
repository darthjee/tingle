# Reporter and full run

Create `python/code_check/rubycritic/reporter.py`, modelled on `file_size.reporter.Reporter`.

**Construction**
- It takes `analyzer`, `target`, `root` and `palette`.
- Display paths follow `file_size`: relative to `target.parent` for a directory, the bare name for a single file.

**Table** (spec §6)
- Columns: `Status`, `Complexity` (2 decimals), `Rating`, `Smells`, `Duplication`, `File`.
- Use `file_size`'s label padding and `─` separator.
- Rows are sorted by complexity descending, ties by path.
- `⛔ PARSE` rows come last, in gray, with `-` cells.

**Filtering**
- `--min-level`, then `--top`, filter only the level rows. PARSE rows are always shown.
- If no level row is left, print `No files at or above <LEVEL>.`

**Summary**
- Print 78 gray `─`, then `Summary: N file(s) | … OK | … WARN | … ERROR | … CRITICAL`, with per-level colours.
- N counts every selected file.
- When k > 0, append ` | k skipped (parse error)`.
- Then print `Score: NN.NN/100 (RubyCritic)`, or `n/a` when the score is null.
- There is no `Total:` line.

**Finishing `CheckRubycritic.run`:**
- Print `Warning: cannot parse <display path>: <message>` on stderr for each `parse_errors` entry, before the report.
- Classify each result with `FileAnalyzer`.
- Render the report.
- Evaluate `--fail-on` over every non-PARSE file and exit 2 when the gate fails, otherwise 0.
- Keep `run` under cyclomatic complexity 10 by pushing the branches into helpers.

**Tests**
- Reporter: sorting, ties, PARSE placement, the `--min-level`/`--top` interaction, the empty-after-filter message, the summary with and without skipped files, a null score, and colours on a fake TTY versus `NO_COLOR`.
- End-to-end executor tests with mocked `which` and `run` and canned JSON: success, gate failure (exit 2), PARSE rows never triggering the gate, invalid JSON, container failure and the mount hint.
- Cover the full spec §11 list.
- Finish with `cd python && ruff check . && pytest`, keeping coverage >= 75%.

## Files to Change
- `python/code_check/rubycritic/reporter.py`: new.
- `python/code_check/rubycritic/executor.py`: parse warnings, report and the gate.
- `python/tests/code_check/rubycritic/test_reporter.py`: new.
- `python/tests/code_check/rubycritic/test_executor.py`: end-to-end cases.
