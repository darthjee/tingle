# Add the rubycritic flags

Append `--exclude`, `--no-default-excludes`, `--no-gitignore`, `--ignore` and
`--include` to `FLAGS`, with the argparse settings and help texts from the
shared contracts. `--exclude`'s help joins rubycritic's `Constants.DEFAULT_EXCLUDES`
(16 names). Completion picks the flags up automatically (`--exclude`,
`--ignore`, `--include` become free-form value flags; the two `store_true`
flags take no value), so `completion.py` needs no change. Update the module
docstring.

## Files to Change
- `python/code_check/rubycritic/flags.py` — five new flag definitions.
