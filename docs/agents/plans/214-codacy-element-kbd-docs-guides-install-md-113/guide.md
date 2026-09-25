# Guide Plan: Codacy: Element: kbd (docs/guides/install.md:113)

Main plan: [plan.md](plan.md)

## Overview
Remove the inline HTML and the padded code span from step 3 of
`docs/guides/install.md`'s "Check that it worked" section. The step must
still tell the user clearly what to type and which key to press.

## Context
Line 113 currently reads:

```markdown
3. Type `tingle ` followed by <kbd>TAB</kbd>. Bash should suggest the
   available command names.
```

Codacy reports two findings on it:

- markdownlint MD033 (no inline HTML) on `<kbd>TAB</kbd>`: #214.
- markdownlint MD038 (spaces inside code span) on `` `tingle ` ``: #215, folded into #214.

The user chose bold text (**Tab**) for the key name. The trailing space moves
out of the code span and is described in words instead.

## Implementation Steps

### Step 1 — Rewrite step 3 of "Check that it worked"
Replace lines 113–114 of `docs/guides/install.md` with:

```markdown
3. Type `tingle`, then a space, then press **Tab**. Bash should suggest the
   available command names.
```

Keep the list's 3-space continuation indent and wrap at about 80 columns,
like the rest of the guide. Don't change anything else in the file.

## Files to Change
- `docs/guides/install.md` — rewrite step 3 of "Check that it worked" (line 113–114) without `<kbd>` and without the trailing space inside the code span.

## Notes
- No CI job lints Markdown (CircleCI only runs `ruff` under `python/`). You can check the fix locally with `grep -n '<kbd>' docs/guides/install.md` (expect no output). If markdownlint is available, run `npx markdownlint-cli docs/guides/install.md` and look for MD033/MD038.
- The PR body should reference both issues (`Fixes #214`, `Fixes #215`) so merging closes both.
