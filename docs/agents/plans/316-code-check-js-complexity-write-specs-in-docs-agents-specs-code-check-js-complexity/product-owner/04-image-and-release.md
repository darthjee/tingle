# image.md and release.md
**`docs/agents/specs/code_check/js_complexity/image.md`** (#318, later extended by #324, #325 and #326) covers:
- the Dockerfile: the exact Node LTS slim tag (Debian, not Alpine), no git, `npm ci` from a pinned `package-lock.json`, and running as an arbitrary uid;
- the entrypoint contract:
  - stdin lines;
  - the **hostile-line rules** (absolute paths, `..`, empty lines, duplicates and missing paths are skipped, each with a `warnings` entry, and each still has a `files` entry);
  - staging under `/tmp/stage/` (symlinks or copies, as decided in step 01);
  - the separate `/tmp/stage-sfc/` tree;
  - nothing written outside `/tmp`;
- the **full merged-JSON contract**:
  - every key and its type;
  - `tool_versions`;
  - the per-file states (normal, parse error, dropped, skipped);
  - the `warnings` entry shape (`tool`, `message`, optional `path`);
  - the rule that `null` means not available and `[]`/0 means empty;
  - the rule that a missing key or a wrong type is unparsable output;
  - the trimmed samples from step 01;
- **pinned tool options**: FTA options, and the placeholders that #324 and #325 fill with the jscpd and escomplex options;
- the encoding and CRLF findings;
- the **fixture list** that #318 must create in `docker/js_complexity/fixture/`, with the expected result per file;
- the local `:dev` build (the `js-complexity-image` Makefile target);
- how to bump versions.

**`docs/agents/specs/code_check/js_complexity/release.md`** (#319) covers:
- the `js_complexity` selector in `scripts/release_image.sh` (`select_image()` settings) and the smoke test;
- the CircleCI jobs `build-and-publish-js-complexity-image` and `update-js-complexity-description`;
- amd64/arm64 and tag resolution;
- the Docker Hub description files and `docs/agents/tingle-js-complexity-image.md`;
- the compatibility invariant: no selector still means `linux`, and the `linux`/`rubycritic` selectors are unchanged;
- the ordering rule: #319 lands before the tag that ships #320.

## Files to Change
- `docs/agents/specs/code_check/js_complexity/image.md` — new.
- `docs/agents/specs/code_check/js_complexity/release.md` — new.
