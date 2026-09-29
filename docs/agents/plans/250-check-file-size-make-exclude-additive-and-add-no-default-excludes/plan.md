# Plan: check_file_size: make --exclude additive and add --no-default-excludes

Issue: [250-check-file-size-make-exclude-additive-and-add-no-default-excludes.md](../../issues/250-check-file-size-make-exclude-additive-and-add-no-default-excludes.md)

## Overview
`--exclude` stops replacing `Constants.DEFAULT_EXCLUDES` and adds to it instead. A new
`--no-default-excludes` flag drops the defaults. `FileCollector` matches exclude names
against the path **relative to `<path>`**, so directories above the target no longer
exclude everything. The normative spec is
[`docs/agents/specs/check_file_size/exclude.md`](../../specs/check_file_size/exclude.md)
(shared contracts in [`README.md`](../../specs/check_file_size/README.md)).

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)

## Shared contracts

- Flags (final names, from spec README section 3):
  - `--exclude a,b`: `type=str`, non-repeatable (last wins), `default=None`. The names
    are **added** to `DEFAULT_EXCLUDES`.
  - `--no-default-excludes`: `action="store_true"`, parsed as `no_default_excludes`,
    default `False`.
- Final exclude list = (`DEFAULT_EXCLUDES` unless `no_default_excludes`) + the
  comma-split, trimmed, non-empty `--exclude` names, deduplicated in order (first
  occurrence kept).
- Matching: whole path component, case-insensitive, against the path relative to
  `<path>` only. Not applied when `<path>` is a single file. Names are not globs.
- Default list, unchanged:
  `node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,.cache,coverage,.nuxt,out,target`.
- Examples every doc must agree on:

  | Invocation | Excluded names |
  |------------|----------------|
  | `tingle check_file_size .` | The defaults |
  | `tingle check_file_size . --exclude fixtures` | The defaults + `fixtures` |
  | `tingle check_file_size . --no-default-excludes` | None (`.git/` is walked too) |
  | `tingle check_file_size . --no-default-excludes --exclude fixtures` | Only `fixtures` |

- Migration note (verbatim in the guide):
  > `--exclude` now **adds** to the default excludes instead of replacing them.
  > `--exclude fixtures` now also skips `node_modules`, `dist`, `build`, etc.
  > For the old behaviour, use `--no-default-excludes --exclude fixtures`.
- Wording: the `--exclude` help text and `long_help` both say "adds to the defaults".
