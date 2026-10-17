# Product-owner Plan: code_check php_complexity: build the tingle_php_complexity Docker image with PDepend (docker/php_complexity/)

Main plan: [plan.md](plan.md)

## Shared contracts

- `docker/php_complexity/` builds `tingle_php_complexity` and is owned by the `shell` agent.
- There is no `docs/agents/tingle-php-complexity-image.md` yet. Link to the spec `specs/code_check/php_complexity/image.md` instead.

## Implementation Steps

### Step 1 — List docker/php_complexity/ in the folder structure
In `docs/agents/folder-structure.md`, extend the `docker/` row (which already names `docker/rubycritic/` and `docker/js_complexity/`) with `docker/php_complexity/` builds `tingle_php_complexity`, linking to [the image spec](specs/code_check/php_complexity/image.md) for now. If the doc has a tree or other listing of `docker/` sub-folders, add the folder there too, with the same wording style as the `js_complexity` entry.

## Files to Change
- `docs/agents/folder-structure.md` — add `docker/php_complexity/` to the `docker/` entry.

## Notes
- Do not create `docs/agents/tingle-php-complexity-image.md`. It belongs to #347.
