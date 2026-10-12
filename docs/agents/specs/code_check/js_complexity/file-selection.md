# Spec: file selection for `tingle code_check js_complexity`

Sub-issues: #321 (selection flags) and #323 (minified bundles). Parent:
#315. Shared contracts: [README.md](README.md).

File selection happens on the host, in Python, before any Docker call. The
selected files are the only ones sent to the container, and the only ones
the tools see. #320 already selects the core extensions minus the default
excludes and declaration files; #321 adds the flags below; #323 adds the
minified skip; #326 adds the SFC extensions. Everything goes through
`docker_check.selection.select_files` (see
[docker-check.md](docker-check.md#25-selection-selectionpy)), which builds
`file_size`'s `FileCollector`. The semantics are `rubycritic`'s.

## 1. Flags (#321)

| Flag | Meaning |
|------|---------|
| `--exclude a,b` | Extra directory names to skip, comma-separated, **added** to the default excludes. Blank entries are dropped. Not repeatable: a second `--exclude` replaces the first (argparse `store`). |
| `--no-default-excludes` | Drop the default excludes **and the minified skip**; only `--exclude` names apply. Declaration files stay skipped. |
| `--ignore GLOB` | Repeatable. Skip files whose path relative to `<path>` matches. |
| `--include GLOB` | Repeatable. Only keep files whose path relative to `<path>` matches at least one include glob. Combines with the extension list: both must match. |
| `--no-gitignore` | Do not skip files ignored by git. |

There is no `--ext`.

Help texts (`rubycritic`'s, scoped to JS/TS):

- `--exclude`: `Extra directory names to skip (comma-separated), added to the defaults: <the 19 names>`
- `--no-default-excludes`: `Do not skip the default directories or minified bundles; only --exclude names apply`
- `--no-gitignore`: `Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)`
- `--ignore`: `Skip files whose path relative to <path> matches this glob (can be repeated)`
- `--include`: `Only analyse JavaScript/TypeScript files whose path relative to <path> matches this glob (can be repeated)`

Before #323, the `--no-default-excludes` help ends at "directories" and the
minified part is added by #323.

## 2. Extensions and skip rules

Matching is case-insensitive, on the file name of the walked path (for a
symlink, the link's name, as for the extension filter).

- **Extensions** (`FileCollector`'s `extensions`, compared with
  `path.suffix.lower()`):
  - core, from #320: `.js .mjs .cjs .jsx .ts .mts .cts .tsx`;
  - SFC, from #326: `.vue .svelte .astro`.
- **Skip rules** (the `skip` predicate of `select_files`), checked on
  `path.name.lower()`:
  - **declaration files**, from #320, always: the name ends with `.d.ts`,
    `.d.mts` or `.d.cts`. No flag or config key turns this off.
  - **minified bundles**, from #323, unless `no_default_excludes` resolves to
    true: the name ends with `.min.js`, `.min.mjs` or `.min.cjs`.
- A file dropped by a skip rule is dropped silently and counted nowhere,
  like a default exclude.

The constants live in `python/code_check/js_complexity/constants.py`:
`EXTENSIONS`, `SFC_EXTENSIONS` (#326), `DECLARATION_SUFFIXES` and
`MINIFIED_SUFFIXES` (#323).

## 3. Default excludes

`file_size`'s `Constants.DEFAULT_EXCLUDES` plus six JS tooling output
directories, in this order (19 names):

```
node_modules, dist, build, .git, vendor, third_party, .next, __pycache__,
.cache, coverage, .nuxt, out, target, .turbo, .svelte-kit, .output,
.vercel, .parcel-cache, storybook-static
```

- They live in `js_complexity/constants.py` as
  `DEFAULT_EXCLUDES = [*file_size Constants.DEFAULT_EXCLUDES, ".turbo", ".svelte-kit", ".output", ".vercel", ".parcel-cache", "storybook-static"]`,
  so a change to `file_size`'s list also applies here. `file_size`'s list
  itself does not change.
- A file is excluded when any component of its path relative to `<path>`
  equals an entry, case-insensitively (the file name is a component too).
- For a single-file `<path>`, the directory excludes (default and
  `--exclude`) do not apply, as in `file_size` and `rubycritic`.
- `--exclude` names are merged after the defaults and deduplicated
  (`code_check.excludes.resolve_excludes`).

## 4. Minified bundles

From #323. The minified skip is a **default exclude** in meaning, even
though it matches a name suffix rather than a path component.

- Skipped by default: names ending in `.min.js`, `.min.mjs`, `.min.cjs`,
  case-insensitively (`app.MIN.JS` too).
- **Only** `--no-default-excludes`, or `"no_default_excludes": true` in the
  config, turns the skip off. It goes together with the directory excludes:
  there is no separate switch.
- **`--include` never brings minified files back.** `--include` only ever
  narrows the selection: `--include '**/*.min.js'` alone selects nothing.
- A **single-file `<path>`** that is minified follows the same rule: it is
  skipped (nothing to analyse, exit 0) unless `--no-default-excludes` is
  given. This differs from the directory excludes, which never apply to a
  single file.
- `.min.ts` or other names are not minified bundles. A minified file without
  `.min` in its name is analysed normally; the guide suggests `--ignore`.
- The image does not skip minified files: with `--no-default-excludes` they
  are analysed (the grounding fixture's `bundle.min.js` scored `6.19` with
  `line_count` 1).

## 5. Filter order

For a directory `<path>`, every regular file found by the walk
(`Path.rglob("*")`) goes through these steps in this order. The first step
that rejects a file drops it.

1. Default excludes (skipped with `--no-default-excludes`).
2. `--exclude` names.
3. `.gitignore` (skipped with `--no-gitignore`).
4. `--ignore` globs.
5. `--include` globs (when given) **and** the extension list.
6. Skip rules: declaration files (always), then minified bundles (unless
   `no_default_excludes`).
7. Symlink confinement (section 7).

Steps 1 to 5 and 7 are `FileCollector`'s, built as
`FileCollector(excludes, extensions, ignore=..., include=..., gitignore=...,
binary_check=False, outside_symlinks=False)`. Step 6 is the `skip`
predicate, applied to `FileCollector.collect`'s result before
`build_selection`. For a single file, steps 1 and 2 do not apply; steps 3 to
7 do.

What does not apply from `file_size`: `--ext` and the `ext` key (the list is
fixed), and the binary check (a file that is not valid UTF-8 must reach the
image and become a `PARSE` row).

## 6. Globs and `.gitignore`

- `--ignore` and `--include` use `file_size`'s `GlobMatcher`:
  `.gitignore`-style globs, case-insensitive, full match against the POSIX
  path relative to `<path>` (`*` stays within one segment, `**` spans
  segments, a leading `/` anchors at `<path>`). For a single-file `<path>`,
  they match the file name. Empty patterns are ignored.
- `.gitignore` is on by default: when `<path>` (or a single file's parent)
  is inside a git work tree, the untracked files git ignores are skipped
  (`.gitignore` files, `.git/info/exclude`, the global excludes file), with
  one `git ls-files --others --ignored --exclude-standard --directory -z`
  call per run on the host. Tracked files are always kept. Without git,
  outside a work tree, or when git fails, nothing is skipped and nothing is
  printed. `--no-gitignore` turns it off. The image has no git.

## 7. Symlinks and single files

- Directory symlinks are not walked (`Path.rglob("*")` does not follow them).
- A selected file whose resolved path is not inside the resolved mount root
  is skipped silently. That covers symlinks to files outside `<path>` and
  dangling symlinks.
- A kept symlink is analysed as its target: the stdin line and the displayed
  path are the target's path relative to the mount root. The selection is
  deduplicated by resolved path, so a symlink and its target count once.
- A single-file `<path>` that is a symlink is resolved first, so the mount
  root is the target's parent.
- The image copies files from `/src` into its staged tree; it never sees a
  symlink that tingle did not resolve (see
  [image.md](image.md#5-staged-tree)).

## 8. Unsendable names

After the filters, the files whose relative path contains `\n` or is not
valid UTF-8 are dropped with a warning (texts in
[subcommand.md](subcommand.md#10-messages)). #320 already does this.

## 9. Docs and tests

#321 and #323 each update, in the same PR:

- the flag help in `python/code_check/js_complexity/flags.py` and the
  `js_complexity` part of `long_help` in `commands/python.json`;
- completion (`--exclude`, `--ignore`, `--include` take free-form values);
- `docs/guides/code_check/js_complexity.md`;
- tests under `python/tests/code_check/js_complexity/`:
  - #321: each flag, the filter order (a file matching several steps is
    dropped by the first), single-file `<path>`, symlinks inside, outside,
    absolute-inside and dangling, upper-case extensions, declaration files
    with every suffix and case;
  - #323: `.min.js/.min.mjs/.min.cjs` in any case skipped by default; kept
    with `--no-default-excludes` and with `"no_default_excludes": true`;
    still skipped with a matching `--include`; a minified single-file
    `<path>` skipped unless `--no-default-excludes`; `.min.ts` kept.

`file_size`'s and `rubycritic`'s selection tests must still pass unchanged.
