# Plan: Codacy: Bare URL used (DOCKERHUB_DESCRIPTION.md:63)

Issue: [212-codacy-bare-url-used-dockerhub-description-md-63.md](../../issues/212-codacy-bare-url-used-dockerhub-description-md-63.md)

## Overview
Convert the two remaining bare URLs in the Links section of
`DOCKERHUB_DESCRIPTION.md` (lines 63 and 64) into labelled Markdown links, so
markdownlint MD034 stops firing. This also resolves #213 (the line 64 finding).

## Context
Codacy's markdownlint (`markdownlint_MD034`, "Bare URL used") flags lines 63
and 64 of `DOCKERHUB_DESCRIPTION.md`. Line 62 was already converted to
`[Repository](https://github.com/darthjee/tingle)` in #211. The file is a
root-level document owned by the architect (see `AGENTS.md`), pushed to Docker
Hub as the full description by `scripts/release_image.sh update-description`.
`docs/agents/tingle-linux-image.md` requires links in this file to be absolute
URLs because Docker Hub cannot resolve repo-relative paths.

## Implementation Steps

### Step 1 — Wrap the bare URLs in labelled links
Replace lines 63–64 of `DOCKERHUB_DESCRIPTION.md`:

```markdown
- `tingle linux` guide: https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md
- Dockerfile: https://github.com/darthjee/tingle/blob/main/shell/linux/Dockerfile
```

with:

```markdown
- [`tingle linux` guide](https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md)
- [Dockerfile](https://github.com/darthjee/tingle/blob/main/shell/linux/Dockerfile)
```

Keep both destinations absolute and unchanged. Do not touch any other line.

## Files to Change
- `DOCKERHUB_DESCRIPTION.md` — lines 63–64: bare URLs become labelled links.

## Notes
- Verify with `grep -nE '(^|[^(<])https?://' DOCKERHUB_DESCRIPTION.md`, which
  should print nothing afterwards.
- The PR must close both issues: include `Fixes #212` and `Fixes #213` in the
  PR description.
- No code, CI, or `docs/agents/` changes are needed. Docker Hub picks up the
  new text on the next release tag.
