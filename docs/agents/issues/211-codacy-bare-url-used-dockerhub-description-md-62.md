# Codacy: Bare URL used (DOCKERHUB_DESCRIPTION.md:62)

## Context

Codacy's markdownlint flagged `DOCKERHUB_DESCRIPTION.md:62` (pattern
`markdownlint_MD034`, category BestPractice, severity Info): "Bare URL used".

Flagged line:

```markdown
- Repository: https://github.com/darthjee/tingle
```

The Links section uses bare URLs, which may not render as links everywhere
and are less readable than labelled links. This file is pushed to Docker Hub
as the image's full description.

## What needs to be done

- Root docs: rewrite the bare URL at `DOCKERHUB_DESCRIPTION.md:62` as a proper
  Markdown link (e.g. `- [Repository](https://github.com/darthjee/tingle)`),
  keeping the same destination.
- Apply the same treatment to the other bare URLs in the same Links section so
  MD034 does not fire on neighbouring lines.
- Make sure the result still renders correctly on Docker Hub (standard
  Markdown links only).

## Acceptance criteria

- [ ] `DOCKERHUB_DESCRIPTION.md:62` uses a Markdown link instead of a bare URL.
- [ ] No bare URLs remain in the `## Links` section of `DOCKERHUB_DESCRIPTION.md`.
- [ ] Link destinations are unchanged.
- [ ] markdownlint MD034 no longer reports `DOCKERHUB_DESCRIPTION.md`.
