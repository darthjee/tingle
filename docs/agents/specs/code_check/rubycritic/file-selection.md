# Spec: file selection for `tingle code_check rubycritic`

Sub-issue: #296. Parent: #290. Shared contracts: [README.md](README.md).

File selection happens on the host, in Python, before any Docker call. The
selected files are the only ones sent to the container. #295 already selects
`.rb` files minus the default excludes; #296 adds the flags below and the
symlink rule. The semantics are `file_size`'s, from
`python/code_check/file_size/file_collector.py`, `glob_matcher.py` and
`git_ignore.py`.

## 1. Flags

| Flag | Meaning |
|------|---------|
| `--exclude a,b` | Extra directory names to skip, comma-separated, **added** to the default excludes. Blank entries are dropped. Not repeatable: as in `file_size`, a second `--exclude` replaces the first (argparse `store`). |
| `--no-default-excludes` | Drop the default excludes; only `--exclude` names apply. |
| `--ignore GLOB` | Repeatable. Skip files whose path relative to `<path>` matches. |
| `--include GLOB` | Repeatable. Only keep files whose path relative to `<path>` matches at least one include glob. Combines with the fixed `.rb` filter: both must match. |
| `--no-gitignore` | Do not skip files ignored by git. |

There is no `--ext`: the `.rb` filter is fixed.

The help texts are `file_size`'s, with "analyse" scoped to Ruby files where it
matters:

- `--exclude`: `Extra directory names to skip (comma-separated), added to the defaults: <the 16 names>`
- `--no-default-excludes`: `Do not skip the default directories; only --exclude names apply`
- `--no-gitignore`: `Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)`
- `--ignore`: `Skip files whose path relative to <path> matches this glob (can be repeated)`
- `--include`: `Only analyse .rb files whose path relative to <path> matches this glob (can be repeated)`

## 2. Default excludes

`file_size`'s `Constants.DEFAULT_EXCLUDES` plus three Ruby-specific names, in
this order (16 names):

```
node_modules, dist, build, .git, vendor, third_party, .next, __pycache__,
.cache, coverage, .nuxt, out, target, tmp, log, .bundle
```

- They live in `python/code_check/rubycritic/constants.py` as
  `DEFAULT_EXCLUDES = [*file_size Constants.DEFAULT_EXCLUDES, "tmp", "log", ".bundle"]`,
  so a change to `file_size`'s list also applies here. `file_size`'s list
  itself does not change.
- A file is excluded when any component of its path relative to `<path>`
  equals an entry, case-insensitively. The file name is a component too, as
  in `file_size`.
- For a single-file `<path>`, path-component excludes (default and
  `--exclude`) do not apply, as in `file_size`.
- `--exclude` names are merged after the defaults and deduplicated
  (`_resolve_excludes` in `file_size`).

## 3. Globs

- `--ignore` and `--include` use `file_size`'s `GlobMatcher`:
  `.gitignore`-style globs, case-insensitive, full match against the POSIX
  path relative to `<path>` (`*` stays within one segment, `**` spans
  segments, a leading `/` anchors at `<path>`).
- For a single-file `<path>`, the globs match the file name.
- Empty patterns are ignored.

## 4. `.gitignore`

- On by default. When `<path>` (or, for a single file, its parent) is inside a
  git work tree, the untracked files git ignores are skipped: `.gitignore`
  files, `.git/info/exclude` and the global excludes file. Tracked files are
  always kept.
- It uses `file_size`'s `GitIgnore.ignored_paths`, one
  `git ls-files --others --ignored --exclude-standard --directory -z` call
  per run, on the host.
- When git is missing, `<path>` is not in a work tree, or git fails, nothing
  is skipped and no message is printed.
- `--no-gitignore` turns it off.
- The image has no git; this step runs only on the host.

## 5. Filter order and `FileCollector`

For a directory `<path>`, every regular file found by the walk
(`Path.rglob("*")`) goes through these steps in order. The first step that
rejects a file drops it.

1. Default excludes (skipped with `--no-default-excludes`).
2. `--exclude` names.
3. `.gitignore` (skipped with `--no-gitignore`).
4. `--ignore` globs.
5. `--include` globs (when given) **and** the `.rb` suffix
   (case-insensitive, `extensions=[".rb"]`).
6. Symlink confinement (section 6).

**Reuse.** `FileCollector` is reused directly, not copied. It gains two
keyword-only arguments whose defaults keep `file_size` unchanged:

| Argument | Default (`file_size`) | `rubycritic` | Effect |
|----------|-----------------------|--------------|--------|
| `binary_check` | `True` | `False` | When `False`, `SkipChecks.is_binary_file` is not called. |
| `outside_symlinks` | `True` (kept) | `False` | When `False`, step 6 applies. |

#295 adds `binary_check` (it needs it from the start); #296 adds
`outside_symlinks`. The rubycritic executor builds it as
`FileCollector(excludes, [".rb"], ignore=..., include=..., gitignore=..., binary_check=False, outside_symlinks=False)`.

**What does not apply from `file_size`:**

- `--ext` and the `ext` config key: the `.rb` filter is fixed.
- The binary check. It would silently drop a `.rb` file that is not valid
  UTF-8, or whose first 1024 bytes end in the middle of a multi-byte
  character. Those files must instead reach the image, which reports them in
  `parse_errors`, so they show as `PARSE` rows.

## 6. Symlinks and unsendable names

**Symlinks.** The container sees only the read-only mount of the mount root,
so a file must resolve to a real file inside it.

- `file_size` today keeps file symlinks wherever they point (`Path.is_file()`
  follows them), and does not walk into directory symlinks
  (`Path.rglob("*")` does not follow them). `file_size` keeps that behaviour.
- `rubycritic` also does not walk into directory symlinks (same walk).
- Step 6: a selected file whose resolved path (`Path.resolve()`) is not inside
  the resolved mount root is skipped silently. This covers symlinks to files
  outside `<path>`, and symlinks whose target does not exist.
- A kept symlink is analysed as its target: the stdin line and the displayed
  path are the target's path relative to the mount root. The selection is then
  deduplicated by resolved path, so a symlink and its target count as one
  file. This also makes absolute symlinks that point inside `<path>` work,
  because the host's absolute path does not exist in the container.
- A single-file `<path>` that is a symlink is resolved first (section 3 of
  [subcommand.md](subcommand.md#3-run-order-preflight-and-pulling)), so the
  mount root is the target's parent.

**Unsendable names.** After the filters, the executor drops, with a warning,
the files whose relative path contains `\n` or is not valid UTF-8. The texts
are in [subcommand.md](subcommand.md#85-unsendable-file-names). #295 already
does this; #296 does not change it.

## 7. Docs and tests

#296 updates, in the same PR:

- the flag help in `python/code_check/rubycritic/flags.py` and the
  `rubycritic` part of `long_help` in `commands/python.json`;
- completion (new flags; `--exclude`, `--ignore`, `--include` take free-form
  values);
- the `rubycritic` section of `docs/guides/code_check.md`;
- tests under `python/tests/code_check/rubycritic/`, covering each flag, the
  filter order (a file matching several steps is dropped by the first),
  single-file `<path>`, symlinks inside, outside, absolute-inside and
  dangling, a non-UTF-8 `.rb` file kept, and `file_size`'s collector tests
  still passing unchanged (new arguments at their defaults).
