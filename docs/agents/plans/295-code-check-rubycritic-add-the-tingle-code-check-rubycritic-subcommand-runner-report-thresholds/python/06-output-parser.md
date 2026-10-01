# Output parser

Create `python/code_check/rubycritic/output_parser.py`:
- `parse(stdout: str, sent_lines: list[str]) -> ParsedOutput`.
- `ParsedOutput` holds `results: dict[str, FileResult]`, `parse_errors: dict[str, str]` and `score: float | None`.
- `FileResult` holds `complexity: float`, `rating: str`, `smells: int` and `duplication: float`.

**Structural checks** (spec §5)
- Invalid JSON, or JSON that fails any check, raises `RubycriticError("could not parse the RubyCritic output")`.
- The checks cover:
  - the top-level object;
  - the `analysed_modules` list;
  - the field types, rejecting `bool` where a number is expected;
  - `score` being a number or null;
  - the `parse_errors` shape.

**Matching paths**
- Strip a leading `/src/` or `./` from each path.
- Match exactly against the sent lines. Entries matching no sent line are ignored.
- If a path appears more than once, the first entry wins.

**Values per file**
- `Smells` counts the smell entries whose type is not in `NON_REEK_SMELL_TYPES`.
- A sent file that is missing from the output becomes `FileResult(0.0, "-", 0, 0)`.
- A file listed in `parse_errors` goes into `parse_errors` and is removed from `results`; `parse_errors` wins over `analysed_modules`.

Tests: one test per structural check, plus path normalisation, unknown entries, duplicate entries, missing files, the smell filter, `parse_errors` precedence and a null score.

## Files to Change
- `python/code_check/rubycritic/output_parser.py`: new.
- `python/tests/code_check/rubycritic/test_output_parser.py`: new.
