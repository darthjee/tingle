# Plan: code_check js_complexity: build the tingle_js_complexity Docker image with FTA (docker/js_complexity/)

Issue: [318-…md](../../issues/318-code-check-js-complexity-build-the-tingle-js-complexity-docker-image-with-fta-docker-js-complexity.md)

## Overview
Add the `docker/js_complexity/` image, which runs FTA only, exactly as
[`image.md`](../../specs/code_check/js_complexity/image.md) pins it:

- a multi-stage Dockerfile (FTA 3.1.0 built from the crate in a pinned Rust stage, an npm `deps` stage, and a pinned `node:24.21.0-slim` final stage);
- an empty-dependency `package.json` and its lock;
- a Node `entrypoint.js` that stages the stdin files and emits the merged JSON;
- the smoke-test fixture and a `make js-complexity-image` target.

`shell` owns all the image work. `product-owner` adds the folder-structure row. The release pipeline, the scripted smoke test and the Docker Hub files stay in #319.

## Agents involved

- [shell](shell.md)
- [product-owner](product-owner.md)

## Shared contracts

- **Folder:** `docker/js_complexity/` is the build context, owned by `shell`.
- **Local image tag:** `tingle_js_complexity:dev`, built by `make js-complexity-image` (`docker build -t tingle_js_complexity:dev docker/js_complexity`).
- **Published name** (#319, for reference only): `darthjee/tingle_js_complexity`.
- **Spec:** `docs/agents/specs/code_check/js_complexity/image.md` is normative. Every version, digest, option, message and JSON key comes from it verbatim.
- **Files** `shell` creates: `Dockerfile`, `package.json`, `package-lock.json`, `entrypoint.js` (with optional `lib/`), `.dockerignore` and `fixture/`. The `DOCKERHUB_*` files are created in #319, not here.
