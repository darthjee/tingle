# Dockerfile and .dockerignore
Write the multi-stage Dockerfile from `image.md` §2, in the style of `docker/rubycritic/Dockerfile`. Start with a header comment that explains the purpose, the contract, the reproducibility pins and the build context, and add stage banners.

- `ARG BASE_IMAGE=node:24.21.0-slim@sha256:d6aa754f16b3197301076f047b5def2f02ea1dbbc2ca920407d46d7ec7f87b20`
- `ARG RUST_IMAGE=rust:1.99.0-slim-bookworm@sha256:2c3a22f0a5533ea2dd5a16627bc841228151faa2d4de2644ac9987e4a2f1f2fa`
- `FROM ${RUST_IMAGE} AS fta`: `RUN cargo install fta --version 3.1.0 --locked --root /opt/fta`.
- `FROM ${BASE_IMAGE} AS deps`: `WORKDIR /opt/tingle_js_complexity`, copy `package.json` and `package-lock.json`, then `RUN npm ci --omit=dev --no-audit --no-fund`.
- `FROM ${BASE_IMAGE}` (final): copy `/opt/fta/bin/fta` to `/usr/local/bin/fta`, `/opt/tingle_js_complexity/` from `deps`, and `entrypoint.js` (plus `lib/` if used) into `/opt/tingle_js_complexity/`. No `apt-get`, no git. Then `USER 1000:1000` and `ENTRYPOINT ["node", "/opt/tingle_js_complexity/entrypoint.js"]`, with no `CMD`.
- `.dockerignore`: `fixture/` only. #319 adds the `DOCKERHUB_*` lines.

## Files to Change
- `docker/js_complexity/Dockerfile` — new.
- `docker/js_complexity/.dockerignore` — new.
