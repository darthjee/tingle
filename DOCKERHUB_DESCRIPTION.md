# tingle

GNU/Linux tool container backing `tingle linux` — provides a non-root,
`ubuntu`-based image with a baseline GNU toolbox (`coreutils`, `findutils`,
`grep`, `sed`, `gawk`, `tar`, `diffutils`) so `tingle linux` subcommands
(`shell`, `sed`, ...) get consistent GNU behavior independent of macOS's BSD
userland.

## Usage

```bash
docker run --rm -v "$(pwd):$(pwd)" -w "$(pwd)" darthjee/tingle:<tag> <command> [args...]
```

Tags are `v`-prefixed semver (e.g. `v1.0.0`), published manually on `v*`
git tag pushes to [darthjee/tingle](https://github.com/darthjee/tingle).
The currently-published tag is pinned in `shell/linux/VERSION`.

Source: [`shell/linux/Dockerfile`](https://github.com/darthjee/tingle/blob/main/shell/linux/Dockerfile).
