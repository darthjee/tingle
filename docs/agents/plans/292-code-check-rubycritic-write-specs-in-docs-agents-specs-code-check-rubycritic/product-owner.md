# Product-owner Plan: code_check rubycritic: write specs in docs/agents/specs/code_check/rubycritic/

Main plan: [plan.md](plan.md)

## Overview
Produce the temporary, normative spec set for the `rubycritic` subcommand of `tingle code_check`. The specs pin every contract shared between the image track (#293 → #294) and the Python track (#295 → #296 → #297), so both can proceed in parallel. The RubyCritic JSON contract must come from a real run, not from assumptions.

## Context
- Parent #290 holds the design decisions: RubyCritic in JSON mode, per-file rows, thresholds on the total Flog complexity (defaults 100/200/400), the `darthjee/tingle_rubycritic` image tagged with the tingle semver, the `--network none` read-only run with the file list on stdin and JSON on stdout, the `rubycritic` config section, and the edge cases.
- Issue #292 lists what each spec must pin, the grounding experiment, the pinned values (default excludes, exact version pins, error message style), and the specs index change. It also records that the `shell` agent owns the new top-level `docker/` folder.
- Precedents:
  - `docs/agents/specs.md` (conventions)
  - the removed `docs/agents/specs/check_file_size/` and `update_command/` spec sets (see git history, e.g. `git show 78eb51b^:docs/agents/specs/check_file_size/README.md`)
- Code and docs to mirror:
  - `python/code_check/file_size/`: `constants.py` (`DEFAULT_EXCLUDES`, thresholds), `executor.py` (flags, the `Error:` style, exit codes), `config.py` (`SCHEMA`/validators), `file_collector.py` (filter order), `reporter.py` (layout)
  - `python/code_check/executor.py` (`SUBCOMMANDS`) and `python/code_check/config.py` (`load_section`)
  - `shell/linux/docker_run.sh` and `shell/linux/VERSION` (how the version is read)
  - `scripts/release_image.sh`, `.circleci/config.yml` (release workflow and tag filter) and `docs/agents/tingle-linux-image.md`
  - `docs/guides/code_check.md`

## Steps

- [01 — Ground the contract in a real RubyCritic run](product-owner/01-ground-rubycritic-json.md)
- [02 — Write README.md (shared contracts)](product-owner/02-readme.md)
- [03 — Write image.md (#293)](product-owner/03-image.md)
- [04 — Write release.md (#294)](product-owner/04-release.md)
- [05 — Write subcommand.md (#295)](product-owner/05-subcommand.md)
- [06 — Write file-selection.md (#296)](product-owner/06-file-selection.md)
- [07 — Write config.md (#297)](product-owner/07-config.md)
- [08 — Register the specs in docs/agents/specs.md](product-owner/08-specs-index.md)

## Notes
- Specs are normative: write "must" / "is", never "could" / "might".
- If the real RubyCritic output contradicts a decision in #290 (a missing field, parse errors not detectable, and so on), state it explicitly in the relevant spec and propose the closest alternative. Never silently drop a column or rule.
- Do not change any code, Dockerfile, CI, guide or agent file. This issue is docs only. Changing `.claude/agents/shell.md` and `docs/agents/folder-structure.md` belongs to #293.
- The experiment needs Docker and network access, to pull `ruby:3.3.N-slim` and install the gem. Its scratch files must not be committed. If Docker is unavailable, stop and report it rather than guessing the JSON shape.
