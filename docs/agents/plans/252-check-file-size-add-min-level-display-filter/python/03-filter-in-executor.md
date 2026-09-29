# Filter and cut rows in the executor
In `CheckFileSize.run`, after `_analyze` and the gate:

```python
shown = [r for r in results if analyzer.reaches(r[1], min_level)]
if args["top"] > 0:
    shown = shown[:args["top"]]
Reporter(analyzer, target, out).report(results, shown, min_level)
```

Move this into a static helper (`_select_shown(analyzer, results, min_level, top)`) to keep `run()` below the complexity limit. The gate stays on the full `results`. Do not reassign `results` for `--top` any more. That reassignment is what made `--top` cut the summary.

## Files to Change
- `python/check_file_size/executor.py` — `_select_shown` helper, pass full results plus shown rows to `Reporter`.
