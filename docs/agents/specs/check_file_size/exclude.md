# Spec: additive `--exclude` and `--no-default-excludes`

Sub-issue: #250. Shared contracts: [README.md](README.md) (flags, precedence,
filter order, exit codes).

## Behaviour

- `--exclude a,b,c` **adds** names to `Constants.DEFAULT_EXCLUDES`. It no
  longer replaces them.
- `--no-default-excludes` drops `DEFAULT_EXCLUDES`. Only the `--exclude`
  names (if any) are then used.
- A file is excluded when any **component of its path relative to `<path>`**
  equals an exclude name, case-insensitively. Whole components only:
  `build` excludes `build/x.js` and `a/build/y.js`, but not `builder/z.js`.
- Components of `<path>` itself and of its parents are **not** checked. This
  fixes the current behaviour, where running inside e.g. `~/build/project`
  excludes every file. It reuses the relative path that #249 computes.
- Path-component excludes do not apply when `<path>` is a single file (see
  README section 5).
- Entries are comma-separated, blanks are trimmed and empty entries are
  dropped (`--exclude ' fixtures, ,tmp'` → `fixtures`, `tmp`).
- The flag stays non-repeatable on the CLI (the last `--exclude` wins, as
  argparse does today). The config `exclude` list is merged with it (README
  section 4).

## Examples

| Invocation | Excluded names |
|------------|----------------|
| `tingle check_file_size .` | The defaults (`node_modules`, `dist`, `build`, `.git`, ...). |
| `tingle check_file_size . --exclude fixtures` | The defaults + `fixtures`. |
| `tingle check_file_size . --no-default-excludes` | None. |
| `tingle check_file_size . --no-default-excludes --exclude fixtures` | Only `fixtures`, which was the old meaning of `--exclude fixtures`. |

## Breaking change and migration

The user guide (`docs/guides/check_file_size.md`) must carry this note:

> `--exclude` now **adds** to the default excludes instead of replacing them.
> `--exclude fixtures` now also skips `node_modules`, `dist`, `build`, etc.
> For the old behaviour, use `--no-default-excludes --exclude fixtures`.

The `long_help` in `commands/python.json` and the `--exclude` help text must
say "adds to the defaults".

## Edge cases

- `--exclude ''` or `--exclude ,` adds nothing.
- A name already in the defaults (`--exclude dist`) is deduplicated, with no
  effect and no error.
- With `--no-default-excludes`, files under `.git/` are walked too. They are
  not in git's ignored set, so `.gitignore` support does not skip them. Use
  `--exclude .git` if needed.
- Names are not globs: `--exclude '*.tmp'` only matches a component literally
  named `*.tmp`. Use `--ignore` for globs.

## Technical decisions

- In `FLAGS`, `--exclude` gets `default: None`. The help text lists the
  defaults and says the names are added to them.
- `--no-default-excludes` is `action: "store_true"`, parsed as
  `no_default_excludes`.
- `executor.py` builds the final list: (`DEFAULT_EXCLUDES` unless
  `no_default_excludes`) + the split `--exclude` names, deduplicated in order.
  It passes that list to `FileCollector`, which keeps receiving one resolved
  `excludes` list and does not know about the defaults.
- `FileCollector._is_excluded` checks the parts of the relative path, not
  `path.parts`.

## Tests expected

- `test_executor.py`: no flag → defaults; `--exclude x` → defaults + `x`;
  `--no-default-excludes` → empty; both → only `x`; blank entries dropped;
  duplicates removed.
- `test_file_collector.py`: a component of `<path>` itself that equals an
  exclude name does not exclude files below it; whole-component,
  case-insensitive match; not applied to a single-file `<path>`.
