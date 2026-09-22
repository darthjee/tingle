# Plan: Codacy: Element: agent (.github/commit_message_template.md:8)

Issue: [117-codacy-element-agent-github-commit-message-template-md-8.md](../../issues/117-codacy-element-agent-github-commit-message-template-md-8.md)

## Overview
Verification-only plan. The MD033 finding at `.github/commit_message_template.md:8` was already fixed on `main` by the fix for #115 (commit 4467456, PR #144). That fix replaced every angle-bracket placeholder in the template with square brackets. No code change is expected.

## Context
Codacy flagged `Co-Authored-By: <agent> agent <AI model email>` because markdownlint MD033 reads `<agent>` as an inline HTML element. Line 8 on `main` now reads `Co-Authored-By: [agent] agent [AI model email]`, and no `<word>`-style placeholders remain in the file. This is the same root cause as #115.

## Implementation Steps

### Step 1 — Verify the template has no angle-bracket placeholders
Run `grep -n '<[a-zA-Z ]*>' .github/commit_message_template.md`. It should return nothing. If it returns any matches, replace them with the `[placeholder]` convention used in the rest of the file.

### Step 2 — Confirm on Codacy and close
After the next Codacy analysis of `main`, confirm that the `markdownlint_MD033` "Element: agent" finding on line 8 is gone. Then close #117 as resolved by #144.

## Files to Change
- None expected. Only `.github/commit_message_template.md` changes, and only if Step 1 finds a leftover angle-bracket placeholder.

## Notes
- The Codacy MCP server was unreachable during planning, so the finding could not be confirmed as cleared against live Codacy data.
- Closing #117 directly as a duplicate of #115 is a reasonable alternative to running this pipeline.
