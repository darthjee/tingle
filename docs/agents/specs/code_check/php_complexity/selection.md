# Spec: file selection for `tingle code_check php_complexity`

Sub-issue: #349 (selection flags). Parent: #344. Shared contracts:
[README.md](README.md).

File selection happens on the host, in Python, before any Docker call. The
selected files are the only ones sent to the container, and the only ones
the tools see. #348 already selects `.php` files minus the default excludes,
Blade templates and `bootstrap/cache`; #349 adds the flags below. Everything
goes through `docker_check.selection.select_files`, which builds
`file_size`'s `FileCollector`. The semantics are `js_complexity`'s.

## 1. Flags (#349)

| Flag | Meaning |
|------|---------|
| `--exclude a,b` | Extra directory names to skip, comma-separated, **added** to the default excludes. Blank entries are dropped. Not repeatable: a second `--exclude` replaces the first (argparse `store`). |
| `--no-default-excludes` | Drop the default excludes **and the `bootstrap/cache` rule**; only `--exclude` names apply. Blade templates stay skipped. |
| `--ignore GLOB` | Repeatable. Skip files whose path relative to `<path>` matches. |
| `--include GLOB` | Repeatable. Only keep files whose path relative to `<path>` matches at least one include glob. Combines with the extension: both must match. |
| `--no-gitignore` | Do not skip files ignored by git. |

There is no `--ext`.

Help texts (`js_complexity`'s, scoped to PHP):

- `--exclude`: `Extra directory names to skip (comma-separated), added to the defaults: <the 16 names, comma-separated>`
- `--no-default-excludes`: `Do not skip the default directories or bootstrap/cache; only --exclude names apply`
- `--no-gitignore`: `Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)`
- `--ignore`: `Skip files whose path relative to <path> matches this glob (can be repeated)`
- `--include`: `Only analyse PHP files whose path relative to <path> matches this glob (can be repeated)`

## 2. Extensions and skip rules

- **Extension** (`FileCollector`'s `extensions`, compared with
  `path.suffix.lower()`): `.php` only (`Constants.EXTENSIONS = [".php"]`).
  `UPPER.PHP` is selected. `.phtml`, `.inc` and `.php3`–`.php8` are not.
- **Skip rules** (the `skip` predicate of `select_files`, section 4).
- A file dropped by a skip rule is dropped silently and counted nowhere,
  like a default exclude.

## 3. Default excludes

`file_size`'s `Constants.DEFAULT_EXCLUDES` plus three PHP directories, in
this order (16 names):

```
node_modules, dist, build, .git, vendor, third_party, .next, __pycache__,
.cache, coverage, .nuxt, out, target, var, storage, .phpunit.cache
```

- They live in `php_complexity/constants.py` as
  `DEFAULT_EXCLUDES = [*file_size Constants.DEFAULT_EXCLUDES, "var", "storage", ".phpunit.cache"]`,
  so a change to `file_size`'s list also applies here. `file_size`'s list
  itself does not change. `vendor` is already in it, so it is not repeated.
- A file is excluded when any component of its path relative to `<path>`
  equals an entry, case-insensitively (the file name is a component too).
- For a single-file `<path>`, the directory excludes (default and
  `--exclude`) do not apply, as in `file_size`, `rubycritic` and
  `js_complexity`.
- `--exclude` names are merged after the defaults and deduplicated
  (`code_check.excludes.resolve_excludes`).
- `bootstrap/cache` is a default exclude in meaning, but it is a skip rule
  (section 4; README deviation 11). `--exclude bootstrap/cache` matches
  nothing, because no single component equals `bootstrap/cache`.

## 4. Skip rules

`php_complexity.selection.select_files(target, root, *, excludes, ignore,
include, gitignore, skip_bootstrap_cache=True)` passes this `skip` predicate
to `docker_check.selection.select_files`. It is called on each walked path
(for a symlink, the link's own path):

1. **Blade templates**, always: `path.name.lower()` ends with `.blade.php`
   (`Constants.BLADE_SUFFIX`). No flag or config key turns this off, and
   `--include '**/*.blade.php'` selects nothing.
2. **`bootstrap/cache`**, when `skip_bootstrap_cache` is true and `target` is
   a directory: the directory components of `path.relative_to(target)`
   (the file name excluded), lower-cased, contain `bootstrap` immediately
   followed by `cache` (`Constants.BOOTSTRAP_CACHE`). So
   `bootstrap/cache/services.php` and `app/Bootstrap/Cache/x.php` are
   skipped; `bootstrap/app.php`, `cache/bootstrap/x.php` and
   `bootstrap/other/cache/x.php` are not.

`CheckPhpComplexity._selection_options` sets
`skip_bootstrap_cache = not bool(options.get("no_default_excludes"))`, the
way `CheckJsComplexity` sets `skip_minified`.

- For a **single-file `<path>`**, rule 1 applies and rule 2 does not (like
  the directory excludes). A Blade file given as `<path>` leaves nothing to
  analyse (exit 0).
- When `<path>` is itself inside a cache directory
  (`tingle code_check php_complexity app/bootstrap/cache`), the relative
  paths have no `bootstrap` component, so rule 2 keeps the files, as the
  excludes do when `<path>` is `vendor/`.

## 5. Filter order

For a directory `<path>`, every regular file found by the walk
(`Path.rglob("*")`) goes through these steps in this order. The first step
that rejects a file drops it.

1. Default excludes (skipped with `--no-default-excludes`).
2. `--exclude` names.
3. `.gitignore` (skipped with `--no-gitignore`).
4. `--ignore` globs.
5. `--include` globs (when given) **and** the extension.
6. Skip rules: Blade templates (always), then `bootstrap/cache` (unless
   `no_default_excludes`).
7. Symlink confinement (section 7).

Steps 1 to 5 and 7 are `FileCollector`'s, built as
`FileCollector(excludes, extensions, ignore=..., include=..., gitignore=...,
binary_check=False, outside_symlinks=False)`. Step 6 is the `skip`
predicate, applied to `FileCollector.collect`'s result before
`build_selection`. For a single file, steps 1 and 2 and the
`bootstrap/cache` rule do not apply; the rest do.

What does not apply from `file_size`: `--ext` and the `ext` key (the
extension is fixed), and the binary check (it is off, as for the other
Docker checks).

## 6. Globs and `.gitignore`

- `--ignore` and `--include` use `file_size`'s `GlobMatcher`:
  `.gitignore`-style globs, case-insensitive, full match against the POSIX
  path relative to `<path>` (`*` stays within one segment, `**` spans
  segments, a leading `/` anchors at `<path>`, a pattern without `/` matches
  in any directory). For a single-file `<path>`, they match the file name.
  Empty patterns are ignored.
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
  [image.md](image.md#5-parse-check-and-staged-tree)).

## 8. Unsendable names

After the filters, the files whose relative path contains `\n` or is not
valid UTF-8 are dropped with a warning (texts in
[cli.md](cli.md#10-messages)). #348 already does this.

## 9. Docs and tests

#349 updates, in the same PR:

- the flag help in `python/code_check/php_complexity/flags.py` and the
  `php_complexity` part of `long_help` in `commands/python.json` (the file
  selection block, listing the Blade and `bootstrap/cache` rules);
- completion (`--exclude`, `--ignore`, `--include` take free-form values);
- `docs/guides/code_check/php_complexity.md`;
- tests under `python/tests/code_check/php_complexity/`:
  - each flag; `--exclude` blank entries and replacement; the filter order
    (a file matching several steps is dropped by the first);
  - `--no-default-excludes` bringing back `vendor/`, `storage/` and
    `bootstrap/cache/` files, but not Blade templates;
  - `--include '**/*.blade.php'` selecting nothing; Blade names in any case
    (`View.BLADE.PHP`);
  - the `bootstrap/cache` rule's positive and negative cases from section 4,
    including `<path>` inside a cache directory and a single file under
    `bootstrap/cache/`;
  - `.gitignore` on and off; single-file `<path>`; symlinks inside, outside,
    absolute-inside and dangling; upper-case extensions.

`file_size`'s, `rubycritic`'s and `js_complexity`'s selection tests must
still pass unchanged.
