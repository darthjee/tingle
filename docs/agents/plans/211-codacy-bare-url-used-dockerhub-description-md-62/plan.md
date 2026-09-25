# Plan: Codacy: Bare URL used (DOCKERHUB_DESCRIPTION.md:62)

Issue: [211-codacy-bare-url-used-dockerhub-description-md-62.md](../../issues/211-codacy-bare-url-used-dockerhub-description-md-62.md)

## Overview

Replace the bare repository URL on `DOCKERHUB_DESCRIPTION.md:62` with a
labelled Markdown link so markdownlint MD034 stops flagging it.

## Context

`DOCKERHUB_DESCRIPTION.md` is a root-level file (architect scope) published
to Docker Hub as the full description of the `tingle linux` image. Its
`## Links` section uses bare URLs. Codacy raised one issue per line: #211
(line 62), #212 (line 63) and #213 (line 64). This plan only covers line 62.

## Implementation Steps

### Step 1 — Turn the repository URL into a Markdown link

Change

```markdown
- Repository: https://github.com/darthjee/tingle
```

to

```markdown
- [Repository](https://github.com/darthjee/tingle)
```

The destination stays the same. Docker Hub renders standard Markdown links,
and the same file already uses this style elsewhere (lines 4, 29, 37, 58).

## Files to Change

- `DOCKERHUB_DESCRIPTION.md` — line 62 only.

## Notes

- Lines 63 and 64 are deliberately left for #212 and #213.
- No CI job lints Markdown locally; Codacy re-checks it on the PR.
