# Plan: check_file_size: write specs for #247 features in docs/agents/specs/

Issue: [248-check-file-size-write-specs-for-247-features-in-docs-agents-specs.md](../../issues/248-check-file-size-write-specs-for-247-features-in-docs-agents-specs.md)

## Overview
Write the specs that the #247 sub-issues implement against. They cover user-visible behaviour **and** the key technical decisions. Also add a permanent specs index (`docs/agents/specs.md`), which stays after #254 removes the `check_file_size` folder.

## Context
- `tingle check_file_size` lives in `python/check_file_size/`:
  - `executor.py`: `FLAGS` list parsed by `common/arg_parser.py`, plus the `--fail-on` gate.
  - `file_collector.py`: `FileCollector(excludes, extensions)`, which walks with `rglob`. It checks path-component excludes, then the `--ext` suffix, then `SkipChecks.is_binary_file`.
  - `constants.py`: `DEFAULT_EXCLUDES` and thresholds.
  - `reporter.py`: the table and summary.
- Current flags: `path`, `--warn/--error/--critical`, `--top`, `--exclude` (comma-separated, **replaces** the defaults, case-insensitive per path component), `--ext` (repeatable, last suffix, case-insensitive), `--fail-on warn|error|critical`.
- Exit codes: 0 ok, 1 error (argparse errors are remapped from 2 to 1), 2 gate failed. Errors go to stderr, and colours only appear on a TTY without `NO_COLOR`.
- Runtime is Python 3.11 (`python/Dockerfile`), so `PurePath.full_match` is not available.
- The user guide is `docs/guides/check_file_size.md`, and `long_help` is in `commands/python.json`.
- Sub-issues: #249 `--ignore`/`--include`, #250 additive `--exclude` + `--no-default-excludes`, #251 `.gitignore` + `--no-gitignore`, #252 `--min-level`, #253 config file, #254 cleanup.

## Steps

- [01 — Add the permanent specs index](product-owner/01-specs-index.md)
- [02 — Write the shared-contracts README](product-owner/02-shared-contracts.md)
- [03 — Write one spec per feature](product-owner/03-feature-specs.md)
- [04 — Link specs from root docs and agent scopes](product-owner/04-root-links.md)

## Notes
- Step 04 touches root-level files (`AGENTS.md`, `CLAUDE.md`, `.claude/agents/product-owner.md`), which belong to `architect`. The architect makes those edits directly, and `product-owner` does steps 01–03.
- No CI job lints markdown. CircleCI only runs Python lint/tests and image builds, so there are no checks to run locally for this issue.
- Keep the specs concise and normative ("must"/"is"). Each feature spec should be readable on its own, without the parent issue.
