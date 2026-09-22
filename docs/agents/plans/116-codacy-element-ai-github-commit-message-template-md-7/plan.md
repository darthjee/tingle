# Plan: Codacy: Element: AI (.github/commit_message_template.md:7)

Issue: [116-codacy-element-ai-github-commit-message-template-md-7.md](../../issues/116-codacy-element-ai-github-commit-message-template-md-7.md)

## Overview
Switch the remaining angle-bracket placeholders in `.github/commit_message_template-2.0.md` to square brackets, so markdownlint MD033 ("no inline HTML") stops flagging them and both commit templates use the same placeholder style.

## Context
The line Codacy originally flagged (`.github/commit_message_template.md:7`) was already fixed by #115 (PR #144). The sibling `.github/commit_message_template-2.0.md` still uses `<...>` placeholders on lines 1, 3, 5, 7 and 8, which markdownlint reads as inline HTML elements. The 2.0 file's content is never parsed at runtime: only its presence matters, because it switches the commit scripts to the two-email behavior. So the change is documentation-only, and the file must keep its path.

## Implementation Steps

### Step 1 — Replace angle-bracket placeholders with square brackets
In `.github/commit_message_template-2.0.md`, rewrite lines 1–8 as:

```
[type]([scope]): [subject] (issue #[id])

[optional body: what was done and why, if not obvious]

Addresses-Comment: [optional: URL of the PR comment this commit addresses]

Co-Authored-By: [AI model name] [AI model email]
Co-Authored-By: [agent] agent [agent email]
```

Leave the explanatory prose (lines 10–30) unchanged. Do not rename or move the file.

### Step 2 — Verify
Run `grep -n '<[A-Za-z]' .github/commit_message_template-2.0.md .github/commit_message_template.md` and confirm there are no matches. If a markdownlint tool is available locally, run it on both files with rule MD033 enabled.

## Files to Change
- `.github/commit_message_template-2.0.md` — switch the placeholders on lines 1, 3, 5, 7 and 8 from `<...>` to `[...]`.

## Notes
- Out of scope: whether arcanum overwrites `commit_message_template-2.0.md` on update (and so whether the fix should also go upstream). The repo owner will handle that separately.
- No CI job lints Markdown, so this is only checked through Codacy.
