# Issue: Codacy: Element: AI (.github/commit_message_template.md:7)

## Description
Codacy's markdownlint flagged `.github/commit_message_template.md:7` (pattern `markdownlint_MD033`, category BestPractice): "Element: AI" on the line:

```
Co-Authored-By: <AI model name> <AI model email>
```

That exact line has **already been fixed** as part of #115 (PR #144), which switched every placeholder in `.github/commit_message_template.md` to square brackets (`[AI model name] [AI model email]`). However, the sibling file `.github/commit_message_template-2.0.md` still uses angle-bracket placeholders on lines 1, 3, 5, 7 and 8, so the same MD033 finding (and its siblings) applies there.

## Problem
markdownlint's MD033 ("no inline HTML") reads angle-bracket placeholders such as `<type>`, `<AI model name>` and `<agent>` as raw HTML elements. `.github/commit_message_template-2.0.md` still uses this style, so it keeps producing Codacy findings, and the two templates now use different placeholder conventions.

## Expected Behavior
- `.github/commit_message_template.md` stays as it is (already compliant).
- `.github/commit_message_template-2.0.md` uses the same square-bracket placeholder convention (`[type]([scope]): [subject] (issue #[id])`, `[AI model name] [AI model email]`, `[agent] agent [agent email]`, etc.), with no MD033 findings.
- The explanatory prose in the 2.0 file (lines 10–30) is left unchanged, and the file stays at the same path, because its presence is what switches the commit scripts to the two-email behavior.

## Solution
Replace each `<...>` placeholder in `.github/commit_message_template-2.0.md` with the matching `[...]` form, the same way #115 did for `.github/commit_message_template.md`. The file's content is never parsed at runtime, so this change is documentation-only.

Out of scope: whether arcanum overwrites `commit_message_template-2.0.md` on update (and so whether the fix should also go upstream). The repo owner will handle that separately.

## Benefits
Clears the remaining MD033 findings for the commit templates and makes both templates use the same placeholder style.
