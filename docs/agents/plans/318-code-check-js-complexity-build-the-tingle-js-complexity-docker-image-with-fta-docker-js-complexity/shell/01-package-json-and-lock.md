# package.json and lock
Create the npm manifest and lock that the `deps` stage installs with `npm ci` (`image.md` §1, §3). In #318 there is **no** npm tool dependency: FTA comes from the Rust stage, and jscpd and escomplex arrive in #324 and #325.

- `package.json`: `"name": "tingle_js_complexity"`, `"private": true`, an `"engines": {"node": "24.21.0"}` entry (or the engine form the spec implies), and no `dependencies`.
- `package-lock.json`: lockfile v3, generated **inside the pinned base image**, e.g.
  `docker run --rm -v "$PWD/docker/js_complexity:/w" -w /w node:24.21.0-slim@sha256:d6aa754f… npm install --package-lock-only`,
  so that npm `11.19.0` writes it. Commit it.

## Files to Change
- `docker/js_complexity/package.json` — new.
- `docker/js_complexity/package-lock.json` — new, generated in the base image.
