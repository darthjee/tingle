# FileCollector binary_check

Add a keyword-only `binary_check: bool = True` argument to `FileCollector.__init__`, after `gitignore`, and store it as `self._binary_check`. In `_accepts(path, rel)` (currently line ~90), change the last line to:

```python
return not (self._binary_check and SkipChecks.is_binary_file(path))
```

`file_size` keeps the default, so its behaviour does not change. rubycritic passes `False` so that non-UTF-8 `.rb` files reach the image and become `PARSE` rows (spec `file-selection.md` §5, `subcommand.md` §7).

Add tests:
- with the default, a binary `.rb` file is still skipped;
- with `binary_check=False`, it is collected;
- both the directory walk and the single-file path go through the flag.

## Files to Change
- `python/code_check/file_size/file_collector.py`: add the new kwarg and gate the binary check on it.
- `python/tests/code_check/file_size/test_file_collector.py`: cover both values of the flag.
