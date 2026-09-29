# Split Reporter into full results vs shown rows
Change `Reporter.report` so the summary is computed from all results and the table from the shown rows. Suggested signature: `report(results, shown=None, min_level="ok")`. `shown=None` means "show `results`", which keeps the old calls working.

- Compute `counts` and `total_lines` from `results`, not from the rows printed. Use `analyzer.classify` for each entry.
- `Summary:` shows `len(results)` file(s).
- If `shown` is empty and `results` is not, skip the table header. Print `No files at or above {min_level.upper()}.` and a blank line instead, then the separator, summary and total as usual.
- To keep the method short, split it into private helpers (`_print_table`, `_print_summary`).

## Files to Change
- `python/check_file_size/reporter.py` — new signature, summary from full results, empty-row note.
