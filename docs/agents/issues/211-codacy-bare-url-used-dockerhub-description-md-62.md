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
- Leave lines 63 and 64 alone: they are tracked separately by #212 and #213.
- Make sure the result still renders correctly on Docker Hub (standard
  Markdown links only).

## Acceptance criteria

- [ ] `DOCKERHUB_DESCRIPTION.md:62` uses a Markdown link instead of a bare URL.
- [ ] Link destinations are unchanged.
- [ ] markdownlint MD034 no longer reports `DOCKERHUB_DESCRIPTION.md:62`.
