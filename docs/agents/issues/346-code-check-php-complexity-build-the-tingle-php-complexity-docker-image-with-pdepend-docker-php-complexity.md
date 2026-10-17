# Issue: code_check php_complexity: build the tingle_php_complexity Docker image with PDepend (docker/php_complexity/)

## Description
Build the `darthjee/tingle_php_complexity` Docker image under `docker/php_complexity/`. It is the analysis runtime for `tingle code_check php_complexity` (parent #344). This first version runs **PDepend only**. Later sub-issues of #344 fill in `functions` (#351) and add jscpd (#352).

**Normative spec:** [`docs/agents/specs/code_check/php_complexity/image.md`](../specs/code_check/php_complexity/image.md). It takes precedence over this body, which only summarises it.

## Problem
Tingle cannot assume PHP or Composer is installed on the host. Like `docker/rubycritic/` for Ruby and `docker/js_complexity/` for JS/TS, the PHP analysis needs a self-contained image with a stable stdin → stdout contract that the Python side can rely on.

## Expected Behavior
### Files (`docker/php_complexity/`, owned by `shell`)
- `Dockerfile`:
  - Two stages. A build-only `deps` stage from the pinned `composer:2.10.3` image (tag + digest in `ARG COMPOSER_IMAGE`) runs `composer validate --no-check-publish` and then `composer install --no-dev --classmap-authoritative`. The final stage uses `php:8.5.11-cli-trixie` (tag + digest in `ARG BASE_IMAGE`; Debian, there is no `-slim` tag).
  - The final stage installs no apt package and contains no git, Composer, `zip` or `unzip`.
  - It ends with `USER 1000:1000` and `ENTRYPOINT ["php", "/opt/tingle_php_complexity/entrypoint.php"]`, with no `CMD`.
- `composer.json` (exactly as in spec §3: `pdepend/pdepend` `3.0.0`, `config.platform.php` `8.5.11`) and `composer.lock`. Both are generated inside the pinned Composer image with `--no-install`, and both are committed.
- `entrypoint.php`, written in **PHP**, optionally with helpers under `lib/`. It uses only the standard library and `vendor/`.
- `fixture/`: the smoke-test fixture, with every file content as given in spec §9.1, including the byte-exact `crlf.php`, `bom.php` and `latin1.php`.
- `.dockerignore`, which excludes `fixture/` and `vendor/`.

### Entrypoint contract (spec §4–§8)
- **Input:** stdin, read as bytes. Stdin that is not valid UTF-8 → exit 1. It is split on `\n`, and nothing is trimmed. There are no arguments.
- **Refused lines**, checked in order: empty, absolute path, `..` segment, duplicate line, not a regular file under `/src` (realpath), extension not `php`, `*.blade.php`. A refused line keeps its `files` entry with `parse_error: false` and every metric set to `null`, and adds an `entrypoint` warning.
- **Parse check:** `token_get_all($code, TOKEN_PARSE)`. A `CompileError` sets `parse_error: true` and adds a `php` warning; the file is not staged.
- **Staged tree:** each accepted file is copied to `/tmp/stage/<n>.php`, where `<n>` is the input line number. PDepend runs over that directory, never over `/src`. Results are mapped back by `<n>`.
- **PDepend run:** `proc_open` with an argument array, cwd `/tmp`, `XDG_CACHE_HOME=/tmp/pdepend-cache`, and `--quiet --summary-xml=/tmp/pdepend/summary.xml /tmp/stage`. PDepend output goes to stderr. It is skipped when nothing was staged.
- **PDepend-reported parse errors:** the entrypoint scans PDepend's stdout error block. Each `file: /tmp/stage/<n>.php` line sets `parse_error: true` on line `<n>`, discards that file's XML data and adds a `pdepend` warning. A line in the block that doesn't match becomes a path-less warning.
- **Output:** one JSON object plus `\n`:
  - `tool_versions`: `php` (`PHP_VERSION`), `pdepend` (`Composer\InstalledVersions`), `jscpd: null`.
  - `files`: one entry per input line, in input order, with `path`, `parse_error`, `pdepend` (`ccn` total, `max_ccn`, `max_npath`, `min_mi`, `lloc`, or `null`), `functions: null` and `duplication: null`.
  - `warnings`, in the order the spec pins.
  - Counted units are class/trait methods and functions that have a `file`. Bare `<method>` elements are ignored.
- **Exit status:** `0` when the JSON was printed. If PDepend exits non-zero, the entrypoint exits with PDepend's status. Any other failure (version unreadable, killed by a signal, missing or malformed XML, unknown path, malformed entry) exits `1` with a `tingle_php_complexity: <reason>` line on stderr. On any failure, nothing goes to stdout. Empty stdin prints empty `files`/`warnings` and exits 0.
- **Runtime:** writes only under `/tmp`. Works with any `--user`, `--network none`, `/src:ro` and `--read-only --tmpfs /tmp`.

### Build and docs
- A `php-complexity-image` target in the `Makefile` (added to `.PHONY`), next to `js-complexity-image`: `docker build -t tingle_php_complexity:dev docker/php_complexity`.
- `docs/agents/folder-structure.md` lists `docker/php_complexity/`, and `.claude/agents/shell.md` adds it to the `shell` agent's scope.

### Verification
- `docker buildx build --platform linux/amd64 docker/php_complexity` and the same command for `linux/arm64` both succeed.
- The spec §9 smoke test is run by hand against `tingle_php_complexity:dev`, with the 25-line stdin, `-v fixture:/src:ro` and `--user 501:20`. The results are recorded in the PR:
  - exit 0 and the versions;
  - 25 entries, with the per-file table and the warnings matching (`min_mi` compared to one decimal; `functions`/`duplication` all `null`);
  - `command -v git` fails;
  - empty stdin prints empty `files`/`warnings` and exits 0;
  - the run also passes under `--network none --read-only --tmpfs /tmp`.

## Solution
Follow `docker/js_complexity/`'s layout and conventions. Implement exactly what `image.md` pins. If something in the spec turns out to be wrong during implementation (for example, if the regenerated lock or a fixture expectation differs), raise it on this issue and update the spec in the same PR. Do not deviate silently.

### Out of scope
- The release pipeline: the `release_image.sh` selector, `smoke_test_php_complexity`, the CircleCI jobs, the Docker Hub descriptions and `docs/agents/tingle-php-complexity-image.md`. These belong to the release sub-issue (#347).
- Filling `functions` (#351) and jscpd/`duplication` (#352).
- The Python CLI side of `code_check php_complexity`.
