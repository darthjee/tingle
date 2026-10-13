# Add the selection flags

Append the five flag dicts to `FLAGS` in `js_complexity/flags.py`, after `--image`, with the shapes and help texts from the shared contract. Copy them from `rubycritic/flags.py`, changing only the `--include` text ("JavaScript/TypeScript files" instead of ".rb files") and taking the defaults from `js_complexity.constants.Constants.DEFAULT_EXCLUDES`. Don't add a shared helper. In the module docstring, add a paragraph like `rubycritic`'s: the selection flags mirror `file_size`'s, there is no `--ext`, and their parsing lives in `code_check.excludes` and `docker_check`.

## Files to Change
- `python/code_check/js_complexity/flags.py` — add the five flags and the docstring paragraph.
