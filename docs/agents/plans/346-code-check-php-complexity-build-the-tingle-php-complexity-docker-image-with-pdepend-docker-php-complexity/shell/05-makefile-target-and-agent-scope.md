# Makefile target and shell agent scope
In the root `Makefile`, add `php-complexity-image` to `.PHONY` and add the target next to `js-complexity-image`, with one recipe line: `docker build -t tingle_php_complexity:dev docker/php_complexity`.

In `.claude/agents/shell.md`, add `docker/php_complexity/` builds `tingle_php_complexity` to the docker-images bullet. Add a paragraph like the `tingle_js_complexity` one: the build context is `docker/php_complexity/`, `make php-complexity-image` produces `tingle_php_complexity:dev`, and version bumps (PHP base image, Composer build image, PDepend) follow [image.md §13](../../docs/agents/specs/code_check/php_complexity/image.md#13-bumping-versions) until #347 adds `docs/agents/tingle-php-complexity-image.md`.

## Files to Change
- `Makefile` — new `php-complexity-image` target and `.PHONY` entry.
- `.claude/agents/shell.md` — scope bullet and build/bump paragraph.
