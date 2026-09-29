# Add the flag and default resolution
Add `--min-level` to `FLAGS` in `executor.py`, next to `--top`: `type: str`, `choices: list(FileAnalyzer.LEVELS)` (or the literal `["ok", "warn", "error", "critical"]`), `default: None`, help text `"Show only files at this level or higher (default: ok)"`. In `run()`, resolve `args["min_level"] or "ok"`.

Check that `FileAnalyzer.reaches(lines, "ok")` returns `True` for any count. It already does, because `LEVELS.index("ok") == 0`. Do not add a second ordering list.

Add examples to the module docstring, e.g. `./check_file_size.py ./src --min-level warn` and `./check_file_size.py ./src --min-level error --top 5`.

## Files to Change
- `python/check_file_size/executor.py` — new `FLAGS` entry, default resolution, docstring examples.
