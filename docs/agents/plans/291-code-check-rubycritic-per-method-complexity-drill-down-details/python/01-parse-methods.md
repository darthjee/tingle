# Parse the `methods` key
In `python/code_check/rubycritic/output_parser.py`:

- Add a frozen dataclass `MethodResult(name: str, line: int, score: float)`.
- Add `methods: dict[str, list[MethodResult]] | None = None` to `ParsedOutput`. `None` means the key was absent.
- Add `_methods(data)`. A missing key returns `None`. Otherwise the value must be a list of dicts with `path` (str), `name` (str), `line` (int, not bool) and `score` (number). Anything else raises `OutputFormatError("unexpected methods")`.
- In `parse`, normalise each path with `normalize_path` and keep only entries whose path is a sent line (and not a parse error). Group them by line, sorted by score descending then name. When the key is present, every sent line without methods maps to nothing; the reporter uses `.get(line, [])`.
- Add a `methods` list to `tests/code_check/rubycritic/sample_output.py`, and add tests: absent key → `None`, malformed entries, path normalisation, grouping and order.

## Files to Change
- `python/code_check/rubycritic/output_parser.py`: `MethodResult`, `_methods`, `ParsedOutput.methods`.
- `python/tests/code_check/rubycritic/sample_output.py`: sample `methods`.
- `python/tests/code_check/rubycritic/test_output_parser.py`: new tests.
