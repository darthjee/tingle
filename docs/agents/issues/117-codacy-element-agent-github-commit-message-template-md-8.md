# Issue: Codacy: Element: agent (.github/commit_message_template.md:8)

## Description
Codacy's markdownlint flagged `.github/commit_message_template.md:8` (pattern `markdownlint_MD033`, category BestPractice): "Element: agent" on the line:

```
Co-Authored-By: <agent> agent <AI model email>
```

## Problem
The commit message template used angle-bracket placeholders (`<type>`, `<agent>`, `<AI model email>`, ...). markdownlint's MD033 ("no inline HTML") treats `<word>` as a raw HTML element. This is the same root cause as #115 (`Element: type`, line 1).

## Expected Behavior
The template keeps its fill-in-the-blank placeholders without tripping MD033, and the Codacy finding at line 8 no longer appears.

## Solution
Already addressed by the fix for #115 (commit 4467456, PR #144), which replaced every angle-bracket placeholder in `.github/commit_message_template.md` with square brackets. Line 8 now reads:

```
Co-Authored-By: [agent] agent [AI model email]
```

Remaining work: confirm on the next Codacy analysis of `main` that the finding is gone, then close this issue as resolved by #144. No code change is expected.

## Benefits
Avoids duplicate work and keeps the issue tracker consistent with the code as it stands.
