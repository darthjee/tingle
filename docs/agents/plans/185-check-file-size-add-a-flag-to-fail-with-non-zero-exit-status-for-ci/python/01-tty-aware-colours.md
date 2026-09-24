# TTY/NO_COLOR-aware colours
Add a small palette helper (e.g. `python/check_file_size/palette.py` with a
`Palette` class built from a stream). It exposes the same names as the
colour constants (`RESET`, `BOLD`, `DIM`, `GREEN`, `YELLOW`, `RED`,
`MAGENTA`, `CYAN`, `GRAY`). These return the ANSI code when
`stream.isatty()` is true and `os.environ.get("NO_COLOR")` is empty, and `""`
otherwise. Guard against streams without `isatty`.

Use it everywhere colour is printed:
- `executor.py`: header, "No files found" message (stdout palette) and the
  path-not-found error (stderr palette, see step 02).
- `reporter.py`: take a palette (constructor arg, defaulting to a stdout
  palette) and use it for the table rows and summary.
- `file_analyzer.py`: `classify` currently returns a raw colour. Either pass a
  palette into `FileAnalyzer` or have `classify` return a level key that the
  reporter maps to a colour through its palette. Keep the emoji labels
  unchanged.

Tests: plain output (no `\033[`) when stdout is not a TTY (pytest's capsys
isn't a TTY) and when `NO_COLOR=1`. Coloured output when a fake stream
reports `isatty() == True` and `NO_COLOR` is unset. Update existing
reporter/analyzer tests that assert on colour codes.

## Files to Change
- `python/check_file_size/palette.py`: new stream-aware colour helper
- `python/check_file_size/constants.py`: keep the raw codes; the docstring notes that they are consumed via the palette
- `python/check_file_size/reporter.py`: use the injected palette
- `python/check_file_size/file_analyzer.py`: decouple the classification colour from the raw constants
- `python/check_file_size/executor.py`: use the stdout/stderr palettes
- `python/tests/check_file_size/test_palette.py`: new tests
- `python/tests/check_file_size/test_reporter.py`, `test_file_analyzer.py`: adjust for the palette
