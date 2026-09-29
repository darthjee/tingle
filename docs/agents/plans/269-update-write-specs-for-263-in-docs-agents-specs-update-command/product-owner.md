# Product-Owner Plan: update: write specs for #263 in docs/agents/specs/update_command/

Main plan: [plan.md](plan.md)

## Overview
Turn the decisions recorded in the body of #263 into normative specs that
#264–#267 implement against and that #270 later removes. The **source of
truth is the live body of #263** (`gh issue view 263`). Read it in full
before writing, and copy its decisions faithfully: approach B, E1–E15 (plus
E9b), S1–S3, the atomicity phases, and latest-release resolution. Do not
re-decide anything.

## Context
- The layout and conventions come from `docs/agents/specs.md`: a shared
  `README.md` plus one file per feature, each readable on its own, written as
  "must" / "is". `AGENTS.md` (Specs section) says the same.
- Precedent: #248 (commit `ee5c2cf`) wrote
  `docs/agents/specs/check_file_size/`. Reuse its README shape (`git show
  ee5c2cf:docs/agents/specs/check_file_size/README.md`): a parent-issue line,
  "this file wins on conflict", then numbered sections (overview table of
  features/specs/sub-issues, merge order, contracts).
- Sub-issues: #269 (these specs) → #264 → #265 → #266 → #267 → #270 (cleanup).
  #264–#266 must be merged before the 0.4.0 tag. The git-clone follow-up
  (#268) is out of scope.
- The folder is `update_command/` (the user's choice, not `update/`).
- There is no separate user-guide spec. The rules for #267 go in the README.

## Steps

- [01 — Write the shared-contracts README](product-owner/01-readme.md)
- [02 — Write manifest-hashes.md (#264)](product-owner/02-manifest-hashes.md)
- [03 — Write installer-update-mode.md (#265)](product-owner/03-installer-update-mode.md)
- [04 — Write update-command.md (#266)](product-owner/04-update-command.md)
- [05 — Add the update_command row to the specs index](product-owner/05-specs-index.md)

## Notes
- No CI job lints Markdown (`.circleci/config.yml` only runs ruff, pytest and
  release jobs), but Codacy runs markdownlint on the repo. Use real headings
  (not bold lines as headings), fenced code blocks with a language, and no
  trailing spaces.
- Each feature spec must end with a **Permanent home** section naming the
  permanent docs its sub-issue must update. #270 checks these before
  deleting the specs.
- Keep edge-case ids (E1–E15, E9b) and safety ids (S1–S3) identical to #263,
  so the sub-issues and PRs can cite them.
- If a spec file would contradict the README, fix the spec: the README wins.
