# Pin jscpd and add the Node build stage
Pin jscpd `5.4.1` for the image and ship only its native binary, per [duplication.md §1](../../../specs/code_check/php_complexity/duplication.md#1-image-changes).

- New `docker/php_complexity/package.json` exactly as in the spec (name `tingle_php_complexity`, private, `engines.node` `24.21.0`, `dependencies.jscpd` `5.4.1`).
- New `docker/php_complexity/package-lock.json` (lockfile v3), generated inside `node:24.21.0-slim` with `npm install --package-lock-only`; it must include `jscpd-linux-x64-gnu` and `jscpd-linux-arm64-gnu` `5.4.1`.
- Dockerfile: add `ARG NODE_IMAGE=node:24.21.0-slim@sha256:d6aa754f…` (same digest as `docker/js_complexity/`) and a `jscpd` stage that runs `npm ci --omit=dev --no-audit --no-fund`, asserts exactly one `node_modules/jscpd-linux-*-gnu` directory, and copies its `bin/jscpd` to `/opt/jscpd/jscpd`. The final stage adds `COPY --from=jscpd /opt/jscpd/jscpd /usr/local/bin/jscpd`. Update the header comment (Reproducibility: jscpd pinned by `package.json` + `package-lock.json`; the final stage has no Node and no `node_modules`).
- `.dockerignore`: add `node_modules/`.

## Files to Change
- `docker/php_complexity/package.json` — new: the jscpd pin.
- `docker/php_complexity/package-lock.json` — new: lockfile v3 with both Linux platform packages.
- `docker/php_complexity/Dockerfile` — Node build stage, copy of the binary, header comment.
- `docker/php_complexity/.dockerignore` — exclude `node_modules/`.
