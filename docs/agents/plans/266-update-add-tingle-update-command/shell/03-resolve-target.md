# Resolve and validate the target version
Add a `validate_version` helper that fails unless the value matches
`^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$` (E6) and is 0.4.0 or later (E2).
Compare numerically on the `X.Y.Z` part: split it on `.` and compare major,
minor, patch as integers. Any `0.4.0-<suffix>` counts as 0.4.0 for the floor.
A version below the floor prints exactly
`tingle update can only install 0.4.0 or later`. Both cases exit non-zero.

- **Pin:** validate it **before any network call**, and use it as the target.
- **Latest:** `curl -sS -w '%{http_code}'` on `<api>/releases/latest` (where
  `<api>` is `${TINGLE_RELEASE_API_URL:-https://api.github.com/repos/<repo>}`),
  with no auth header. 200: read `.tag_name` with `jq -r` and validate it the
  same way. 403 or 429: a rate limit. A curl failure, another status or an
  empty or `null` `tag_name`: an error. All errors print a message that
  suggests pinning a version (`tingle update X.Y.Z`) and exit non-zero (E8).
- Support `file://` for the test hooks. curl reports no HTTP status for
  `file://`, so treat a successful curl with status `000` as 200, and a failed
  one as not found or a network error.

## Files to Change
- `shell/update/executor.sh` — `validate_version` and target resolution.
