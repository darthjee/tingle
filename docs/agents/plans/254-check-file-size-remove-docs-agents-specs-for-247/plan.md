# Plan: check_file_size: remove docs/agents/specs/ for #247

Issue: [254-check-file-size-remove-docs-agents-specs-for-247.md](../../issues/254-check-file-size-remove-docs-agents-specs-for-247.md)

## Overview
This is the last sub-issue of #247. Every `check_file_size` feature is merged (#249–#253, PRs #256–#260), so the temporary specs under `docs/agents/specs/check_file_size/` can go. First the `guide` agent confirms that `docs/guides/check_file_size.md` covers everything the specs define, and fills any gap. Then the `product-owner` agent deletes the specs, updates the permanent index `docs/agents/specs.md`, and replaces the `AGENTS.md` example that points at the deleted folder. No code changes.

## Agents involved

- [guide](guide.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Order:** `guide` finishes before `product-owner` deletes anything. The specs are the reference for the coverage check.
- **Scope of the coverage check.** Everything in the six spec files (`README.md`, `config.md`, `exclude.md`, `gitignore.md`, `ignore-include.md`, `min-level.md`):
  - Features: `--ignore` / `--include` (glob syntax, repeatable, combined with `--ext`), additive `--exclude` + `--no-default-excludes`, `.gitignore` + `--no-gitignore` (skipped silently when git or a repo isn't available), `--min-level` (display only; the summary and `--fail-on` still count every file).
  - Config file: `~/.tingle/code_check/config.json` (`check_file_size` section, every key), `--no-config`, the `Config:` header line.
  - Contracts: filter order (default excludes → `--exclude` → `.gitignore` → `--ignore` → `--include`/`--ext` → binary check), CLI-vs-config precedence (scalars are overridden, lists are merged), exit codes (invalid JSON or unknown keys → stderr, exit 1).
- **Nothing links to the deleted folder afterwards.** `git grep specs/check_file_size` must return no tracked files, apart from ignored or untracked files under `docs/agents/issues/`.
- **The PR closes both issues:** its body includes `Fix #254` and `Closes #247`.
