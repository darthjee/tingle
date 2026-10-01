# Print the detail lines
In `reporter.py`:

- `report(parsed, min_level, top, details=None)`.
- In `_print_table`, after each level row, when `details is not None`: take `parsed.methods.get(line, [])`. Slice it to `[:details]` when `details > 0`, and print each method using the layout in plan.md, in `c.DIM` (or `c.GRAY`). Don't print detail lines under PARSE rows.
- Rows hidden by `--top`/`--min-level` get no details, because only the shown rows are iterated.
- Tests in `test_reporter.py`: lines appear only with `details`, limit N, 0 = all, file with no methods, ordering, alignment, colourless output without a TTY.

## Files to Change
- `python/code_check/rubycritic/reporter.py`: detail lines.
- `python/tests/code_check/rubycritic/test_reporter.py`: tests.
