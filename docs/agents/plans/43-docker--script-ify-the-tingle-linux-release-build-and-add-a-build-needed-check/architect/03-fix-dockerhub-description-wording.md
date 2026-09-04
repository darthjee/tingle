# Tighten DOCKERHUB_DESCRIPTION.md's tag wording

`DOCKERHUB_DESCRIPTION.md` currently reads (line 15):

> Tags follow plain semver (e.g. `v1.0.0`), published manually on `v*` git
> tag pushes to [darthjee/tingle](https://github.com/darthjee/tingle).

The example (`v1.0.0`) is already correct — `v`-prefixed, matching what CI
actually produces — but calling it "plain semver" while showing a
`v`-prefixed example is self-contradictory (plain semver has no `v`
prefix). Reword to remove the contradiction and name
`shell/linux/VERSION` as the pin file backing the currently-published tag,
e.g.:

> Tags are `v`-prefixed semver (e.g. `v1.0.0`), published manually on `v*`
> git tag pushes to [darthjee/tingle](https://github.com/darthjee/tingle).
> The currently-published tag is pinned in `shell/linux/VERSION`.

## Files to Change
- `DOCKERHUB_DESCRIPTION.md` — reword the tag-convention line as above.
