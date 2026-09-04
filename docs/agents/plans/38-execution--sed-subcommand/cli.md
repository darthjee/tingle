# cli Plan: Execution: sed subcommand

Main plan: [plan.md](plan.md)

## Shared contracts

Document exactly the invocation and examples `shell` implements (see
`plan.md`'s "Shared contracts" for the full list):

- `tingle linux sed <sed-args...>` — forwards verbatim to `sed` inside
  the container.
- Piped-stdin usage: `cat file | tingle linux sed 's/a/b/'`.
- In-place edit: `tingle linux sed -i 's/foo/bar/' somefile.txt` (GNU
  `-i` syntax).

## Implementation Steps

### Step 1 — Document `sed` in `commands/shell.json`'s `long_help`

Extend the `linux` entry's `long_help` in `commands/shell.json` with a
`sed` usage line under `Usage:` (already lists `tingle linux shell` and
`tingle linux sed <sed-args...>`) and add an `Examples:` block entry for
`sed`, following the existing `shell` example's style — including one
example showing the in-place edit (`tingle linux sed -i 's/foo/bar/'
somefile.txt`) and one showing piped-stdin usage
(`cat file | tingle linux sed 's/a/b/'`).

## Files to Change

- `commands/shell.json` — add `sed` examples to the `linux` entry's
  `long_help`.

## Notes

- No CI job currently lints/tests `commands/` (`.circleci/config.yml`'s
  `lint`/`tests` jobs only cover `python/`), so no `## CI Checks` section
  applies here.
- Purely a documentation/help-text change — no behavior change on the
  `cli` side.
