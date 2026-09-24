# Plan: Docker: set Docker Hub short description, refresh DOCKERHUB_DESCRIPTION.md and harden update-description

Issue: [182-docker-add-docker-hub-description-for-darthjee-tingle-and-push-it.md](../../issues/182-docker-add-docker-hub-description-for-darthjee-tingle-and-push-it.md)

## Overview
Add a repo-root `DOCKERHUB_SHORT_DESCRIPTION.txt` holding the one-line Docker
Hub summary. Refresh `DOCKERHUB_DESCRIPTION.md`. Change
`scripts/release_image.sh update-description` so it sends both fields in one
PATCH and fails loudly on missing files, an over-long summary, or HTTP errors.
The existing `update-description` CircleCI job pushes the result on the next
release tag, so no CI or manual push changes are needed.

## Agents involved

- [shell](shell.md): the Bash release script and the two image description
  files
- [product-owner](product-owner.md): `docs/agents/tingle-linux-image.md`

## Shared contracts

- **Short description file**: `DOCKERHUB_SHORT_DESCRIPTION.txt` at repo root.
  It holds a single line of plain text; a trailing newline is allowed and is
  stripped before sending. The trimmed content must be 1–100 characters.
- **Full description file**: `DOCKERHUB_DESCRIPTION.md` at repo root
  (unchanged path), in Markdown.
- **API call**: `PATCH https://hub.docker.com/v2/repositories/darthjee/tingle/`
  with JSON body `{"description": <short>, "full_description": <full>}`,
  authenticated with the JWT from `POST /v2/users/login/`.
- **Failure semantics**: `update-description` exits non-zero when either file
  is missing, when the short description is empty or longer than 100
  characters, or when the login or PATCH HTTP call fails.
