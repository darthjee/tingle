# Declare the selection flags
Add the five flags from the shared-contracts table to `FLAGS`, after `--image` and in the table's order. Copy the shape of `js_complexity/flags.py`: the `--exclude` help lists `','.join(Constants.DEFAULT_EXCLUDES)`, and the `--include` help says "PHP files". Do not add `--no-config` (that is #350) or `--ext`.

## Files to Change
- `python/code_check/php_complexity/flags.py` — add `--exclude`, `--no-default-excludes`, `--no-gitignore`, `--ignore` and `--include`.
