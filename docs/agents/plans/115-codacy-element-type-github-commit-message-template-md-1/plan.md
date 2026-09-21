# Plan: Codacy: Element: type (.github/commit_message_template.md:1)

Issue: [115-codacy-element-type-github-commit-message-template-md-1.md](../../issues/115-codacy-element-type-github-commit-message-template-md-1.md)

## Overview
`.github/commit_message_template.md` uses angle-bracket placeholders (`<type>`, `<scope>`, etc.), which markdownlint's MD033 rule flags as inline HTML. Replace every angle-bracket placeholder in the file with the equivalent square-bracket form so the template stays clear while no longer tripping the linter.

## Context
Codacy flagged `.github/commit_message_template.md:1` (`markdownlint_MD033`) because `<type>(<scope>): <subject> (issue #<id>)` is syntactically indistinguishable from an HTML tag. The same angle-bracket convention is used throughout the rest of the file (`<optional body...>`, `<optional: URL...>`, `<AI model name>`, `<AI model email>`, `<agent>`). No other doc in the repo references this template's placeholder syntax, so only this one file needs updating.

## Implementation Steps

### Step 1 — Replace angle-bracket placeholders with square brackets
In `.github/commit_message_template.md`, replace every angle-bracket placeholder with the same text wrapped in square brackets instead:
- `<type>` → `[type]`
- `<scope>` → `[scope]`
- `<subject>` → `[subject]`
- `<id>` → `[id]`
- `<optional body: what was done and why, if not obvious>` → `[optional body: what was done and why, if not obvious]`
- `<optional: URL of the PR comment this commit addresses>` → `[optional: URL of the PR comment this commit addresses]`
- `<AI model name>` → `[AI model name]`
- `<AI model email>` → `[AI model email]`
- `<agent>` → `[agent]`

Keep the surrounding text and line structure unchanged — only the bracket style changes.

## Files to Change
- `.github/commit_message_template.md` — replace all angle-bracket placeholders with square-bracket placeholders.

## Notes
- No other docs reference this template's angle-bracket syntax, so no follow-up doc updates are needed.
- No local CI job runs markdownlint for this repo; Codacy re-analyzes on push, so verification happens on the next Codacy scan of the PR.
