# Makefile target and shell agent scope
- `Makefile`: add `js-complexity-image` to `.PHONY` and add the target next to `rubycritic-image`:
  ```make
  js-complexity-image:
  	docker build -t tingle_js_complexity:dev docker/js_complexity
  ```
- `.claude/agents/shell.md`: name `docker/js_complexity/` (it builds `tingle_js_complexity`) in the scope bullet, next to `docker/rubycritic/`. Add a short paragraph after the rubycritic one: the build context is `docker/js_complexity/`, `make js-complexity-image` produces `tingle_js_complexity:dev`, and version bumps follow `image.md` §13 (later `docs/agents/tingle-js-complexity-image.md`, #319).

## Files to Change
- `Makefile` — new `js-complexity-image` target.
- `.claude/agents/shell.md` — scope mentions `docker/js_complexity/`.
