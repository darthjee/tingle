# Output parser
Implement `output_parser.py` per cli.md §5: `parse(stdout, sent_lines)` returns `ParsedOutput` with one `FileResult` per sent file. It maps container paths back to host paths using the sent line order, and a result with `parse_error: true` becomes a `PARSE` file. It raises `OutputFormatError(reason)` on any shape check failure, for example a `files` length or path mismatch, `parse_error` with a non-null `pdepend`, booleans given as numbers, or an unknown `warnings[].tool`. Keep a `max_npath` above 2^53 as an exact int. Ignore the `functions` and `duplication` fields, or carry them through without using them; they are used in #351 and #352.

Add `sample_output.py` (merged JSON built from the grounding fixture) and `test_output_parser.py`, covering every case in the cli.md §11 parsing list.

## Files to Change
- `python/code_check/php_complexity/output_parser.py` — new
- `python/tests/code_check/php_complexity/sample_output.py` — new fixture data
- `python/tests/code_check/php_complexity/test_output_parser.py` — new
