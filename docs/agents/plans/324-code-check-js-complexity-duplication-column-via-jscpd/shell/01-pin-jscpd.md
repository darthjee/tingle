# Pin jscpd 5.4.1
Add `"dependencies": {"jscpd": "5.4.1"}` (exact, no range) to `docker/js_complexity/package.json`. Regenerate `package-lock.json` with Node 24.21.0/npm, for example `npm install --package-lock-only --save-exact jscpd@5.4.1` inside `docker/js_complexity`. Then check that the lock lists both `node_modules/jscpd-linux-x64-gnu` and `node_modules/jscpd-linux-arm64-gnu` at `5.4.1`, as image.md section 3 ("Pinned versions") requires. Update the Dockerfile header comment if it describes the npm tools.

## Files to Change
- `docker/js_complexity/package.json` — add the exact `jscpd` dependency.
- `docker/js_complexity/package-lock.json` — regenerate it, with both linux platform packages.
- `docker/js_complexity/Dockerfile` — update the comments only, if needed (`npm ci` already installs the locked tools).
