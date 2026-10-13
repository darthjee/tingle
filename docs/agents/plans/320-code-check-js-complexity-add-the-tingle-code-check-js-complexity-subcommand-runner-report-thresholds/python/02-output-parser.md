# Parse the merged JSON
Add `python/code_check/js_complexity/output_parser.py` implementing spec §5: `parse(stdout, sent_lines) -> ParsedOutput`. It raises `OutputFormatError(reason)` with the **first** failing check's reason, word for word from the spec §5 table:
- `invalid JSON: <error>`;
- `expected a JSON object`;
- `unexpected tool_versions`;
- `files do not match the sent lines`;
- `unexpected files entry: <i>`;
- `unexpected warnings`.

Rules:
- JSON booleans are never numbers or ints (`isinstance(x, bool)` excluded). Unknown extra keys are ignored.
- `files[i].path` must equal `sent_lines[i]`. Map entry `i` to sent line `i`.
- `parse_error: true` requires `fta`, `duplication` and `functions` to be `null`.
- Validate `duplication` (`null` or `{"lines": int ≥ 0}`) and `functions` (`null` or a list of `{name: str, line/cyclo/sloc: int ≥ 1}`), even though #320 does not display them. Keep them on the per-file result for #324/#325.
- `warnings`: a list of `{tool ∈ {entrypoint, fta, jscpd, escomplex}, message: str, path?: str}`.

Result model (dataclasses, like rubycritic's):
- a per-file result with `line`, `score` (`s = round(fta.score, 1)`, or `0.0` when `fta` is `null`), `cyclo`, `lines` and `assessment` (`None` when `fta` is `null`), plus the raw `duplication`/`functions`;
- the set or dict of `PARSE` lines with their messages (from the `warnings` entry with the same `path` and `tool` `fta` or `entrypoint`, else `unknown error`);
- the refused-line warnings (`warnings` entries whose `path` is a non-parse-error file with `fta: null`, in `warnings` order);
- `tool_versions`.

Keep the module small and flat. If it grows past what Codacy's complexity limits tolerate, split the validators into helper functions, as `rubycritic/output_parser.py` does.

Tests:
- `sample_output.py`: a merged JSON sample copied from [image.md §7](../../specs/code_check/js_complexity/image.md#7-merged-json), with `duplication`/`functions` filled and `null` variants.
- `test_output_parser.py`: every reason, the `files` length and path mismatches, `parse_error` with a non-null `fta`, booleans as numbers or ints, extra keys ignored, rounding (`59.96` → `60.0`), `fta: null` → `0.0`, the parse-error message lookup and the `unknown error` fallback.

## Files to Change
- `python/code_check/js_complexity/output_parser.py`: new.
- `python/tests/code_check/js_complexity/sample_output.py`: new.
- `python/tests/code_check/js_complexity/test_output_parser.py`: new.
