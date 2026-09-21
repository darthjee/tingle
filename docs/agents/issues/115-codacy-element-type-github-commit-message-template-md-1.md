# Issue: Codacy: Element: type (.github/commit_message_template.md:1)

## Description
Codacy's markdownlint flagged `.github/commit_message_template.md:1` (pattern `markdownlint_MD033`, category BestPractice): "Element: type" on the line:

```
<type>(<scope>): <subject> (issue #<id>)
```

## Problem
`.github/commit_message_template.md` is a commit message template that uses angle-bracket placeholders (e.g. `<type>`, `<AI model name>`, `<agent>`) to mark fill-in-the-blank fields. markdownlint's MD033 ("no inline HTML") interprets these bracketed tokens as raw HTML elements, since `<word>` is syntactically indistinguishable from an HTML tag in Markdown.

## Expected Behavior
The commit message template conveys the same fill-in-the-blank placeholders without tripping the "inline HTML" linter — while still being immediately clear to a human or agent filling out a commit message.

## Solution
Replace every angle-bracket placeholder in `.github/commit_message_template.md` with square brackets, e.g. `<type>` → `[type]`, `<AI model name>` → `[AI model name]`, `<agent>` → `[agent]`, and so on for every remaining placeholder in the file (scope, subject, id, optional body, PR comment URL, AI model email). Update all occurrences consistently. No other docs in the repo reference this template's angle-bracket syntax, so no further doc updates are needed.

## Benefits
Resolves the Codacy finding while keeping the template's placeholders clear and easy to fill in.
