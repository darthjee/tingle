# tingle_rubycritic

The [RubyCritic](https://github.com/whitesmith/rubycritic) image behind the
`tingle code_check rubycritic` command of
[tingle](https://github.com/darthjee/tingle). It runs RubyCritic (Flog, Flay
and Reek) on a list of Ruby files and prints the report as one JSON object,
so tingle can check code complexity without a local Ruby setup.

Supported platforms: `linux/amd64`, `linux/arm64`.

## What it contains

| Component | Version |
|-----------|---------|
| Ruby | `3.3.12` (`ruby:3.3.12-slim`, pinned by digest) |
| RubyCritic | `5.0.0` |

Every gem (Flog, Flay, Reek, parser, ...) is pinned by a committed
`Gemfile.lock`. The image has no git and no compiler, so RubyCritic computes
no churn.

## Contract

- **stdin:** one file path per line, relative to the working directory
  (`/src`). Blank lines are ignored; duplicates are kept once.
- **stdout:** exactly one JSON object: RubyCritic's `report.json` plus a
  top-level `parse_errors` list. Files that can't be parsed (syntax errors,
  invalid UTF-8, missing files) are listed there as `{"path", "message"}`
  and are not analysed, so one broken file doesn't abort the whole run.
  With no analysable file, it prints
  `{"metadata":null,"analysed_modules":[],"score":null,"parse_errors":[...]}`.
- **stderr:** RubyCritic's own output and any error message.
- **exit status:** `0` when the JSON was printed (even with parse errors),
  non-zero otherwise.

The image works under any `--user <uid>:<gid>`, with no network and a
read-only `/src`. It only writes under `/tmp`.

## Usage

### Through `tingle code_check rubycritic` (preferred)

Install [tingle](https://github.com/darthjee/tingle) and run:

```bash
tingle code_check rubycritic <path>
```

### Directly with Docker

The canonical run line:

```bash
find . -name '*.rb' | docker run --rm -i --pull never --network none \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  -v "$PWD:/src:ro" -w /src darthjee/tingle_rubycritic:<tag>
```

## Tags

- Tags are plain semver (for example `1.0.0`): the same string as the
  matching tingle release and `X.Y.Z` git tag. tingle `X.Y.Z` uses
  `darthjee/tingle_rubycritic:X.Y.Z` by default.
- Every tingle release tag publishes this image, as one multi-platform
  manifest. There is no `latest` tag.
- The current tag is pinned in
  [`shell/linux/VERSION`](https://github.com/darthjee/tingle/blob/main/shell/linux/VERSION).

## Links

- [Repository](https://github.com/darthjee/tingle)
- [Dockerfile](https://github.com/darthjee/tingle/blob/main/docker/rubycritic/Dockerfile)
