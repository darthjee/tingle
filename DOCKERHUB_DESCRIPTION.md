# tingle

The GNU toolbox image behind the `tingle linux` command of
[tingle](https://github.com/darthjee/tingle). It gives `tingle linux`
subcommands (`shell`, `sed`, ...) consistent GNU behavior, independent of
the BSD userland shipped with macOS.

Supported platforms: `linux/amd64`, `linux/arm64`.

## What it contains

Built on `ubuntu:24.04` with a baseline GNU toolbox:

- `coreutils`
- `findutils`
- `grep`
- `sed`
- `gawk`
- `tar`
- `diffutils`

The image runs as the non-root user `tingle` (uid 1000), so files touched
through a volume mount stay owned by your user on the host.

There is no `CMD` or `ENTRYPOINT`: every run supplies its own command.

## Usage

### Through `tingle linux` (preferred)

Install [tingle](https://github.com/darthjee/tingle) and run:

```bash
tingle linux sed --version
tingle linux shell
```

See the
[`tingle linux` guide](https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md)
for all subcommands and options.

### Directly with Docker

```bash
docker run --rm -v "$PWD:$PWD" -w "$PWD" darthjee/tingle:<tag> <cmd> [args...]
```

For example:

```bash
docker run --rm -v "$PWD:$PWD" -w "$PWD" darthjee/tingle:<tag> sed --version
```

## Tags

- Tags are plain semver (for example `1.0.0`), the same string as the
  matching `X.Y.Z` git tag.
- Images are built and published by CircleCI when that git tag is pushed.
- The current tag is pinned in
  [`shell/linux/VERSION`](https://github.com/darthjee/tingle/blob/main/shell/linux/VERSION).

## Links

- [Repository](https://github.com/darthjee/tingle)
- [`tingle linux` guide](https://github.com/darthjee/tingle/blob/main/docs/guides/linux.md)
- [Dockerfile](https://github.com/darthjee/tingle/blob/main/shell/linux/Dockerfile)
