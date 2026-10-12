# Product-owner Plan: code_check js_complexity: write specs in docs/agents/specs/code_check/js_complexity/

Main plan: [plan.md](plan.md)

## Overview
Write the specs for `tingle code_check js_complexity` under `docs/agents/specs/code_check/js_complexity/`, following `docs/agents/specs.md`'s conventions and the rubycritic precedent (#292, PR #299). Ground them first in real FTA, jscpd and typhonjs-escomplex output, and index them in `docs/agents/specs.md`.

## Context
- #315 is the epic. Its sub-issues are #316 (this issue), #317 (docker_check refactor), #318 (image), #319 (release), #320 (core), #321 (selection), #322 (config), #323 (minified), #324 (jscpd), #325 (`--details`), #326 (SFC) and #327 (cleanup).
- The issue file is the source of truth for every rule the specs pin. In particular, its **Decided choices**, **Additional edge cases** and **Backward compatibility** sections are normative and must be reflected verbatim in substance.
- The specs are normative ("must"/"is"). They take precedence over the sibling issue bodies. Every change compared with #315 goes into a **Deviations from #315** section in `README.md`.
- The current code to describe accurately:
  - `python/code_check/rubycritic/`: `docker_runner.py`, `image.py`, `selection.py`, `executor.py`, `config.py`, `constants.py`, `errors.py`, `output_parser.py`, `reporter.py`, `flags.py`
  - `python/code_check/file_size/` (`FileCollector`, `DEFAULT_EXCLUDES`)
  - `python/code_check/excludes.py`, `python/code_check/validators.py`, `python/code_check/subcommands.py`
  - `scripts/release_image.sh` (`select_image()`), `.circleci/config.yml`, `Makefile`
  - `docker/rubycritic/`
- Style reference: the rubycritic specs as they were at commit `9d5d291`. Read them with `git show 9d5d291:docs/agents/specs/code_check/rubycritic/<file>`.

## Steps

- [01 — Grounding run](product-owner/01-grounding-run.md)
- [02 — README.md: shared contracts, sub-issue map, deviations](product-owner/02-readme.md)
- [03 — docker-check.md](product-owner/03-docker-check.md)
- [04 — image.md and release.md](product-owner/04-image-and-release.md)
- [05 — subcommand.md, file-selection.md, config.md](product-owner/05-subcommand-selection-config.md)
- [06 — duplication.md, details.md, sfc.md](product-owner/06-duplication-details-sfc.md)
- [07 — specs.md index and verification](product-owner/07-index-and-verification.md)

## CI Checks
- There is no CI job for docs. CI runs only `ruff check .` and `pytest` in `python/` (jobs `lint` and `tests`), and this issue touches no Python.

## Notes
- **Docker is required** for step 01. If it is unavailable, stop and report; do not write specs from assumptions.
- Never commit the grounding fixture or tool output. Use a scratch directory outside the repo, e.g. `$(mktemp -d)`.
- If real tool output contradicts a decision (e.g. FTA can't be run on a staged symlink tree, or jscpd has no per-file data), record it in "Deviations from #315" and propose the closest alternative. Never silently drop a rule.
- The final diff must touch only `docs/agents/specs/code_check/js_complexity/**` and `docs/agents/specs.md`.
