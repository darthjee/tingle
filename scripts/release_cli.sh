#!/usr/bin/env bash
#
# release_cli.sh — build and publish the tingle release zip
# (dist/tingle-<tag>.zip + dist/tingle-<tag>.zip.sha256) to a GitHub Release.
#
# Usage:
#   scripts/release_cli.sh build [<tag>]
#   scripts/release_cli.sh publish [--dry-run] [<tag>]
#
# Tag resolution: $CIRCLE_TAG when set (CI), else a positional <tag> argument
# (local dev). Plain semver X.Y.Z (X.Y.Z-<suffix> allowed), no "v" prefix.
#
# Zip content: the INCLUDES allowlist (bin commands completions shell python
# node README.md LICENSE) tracked by git, minus python/tests/,
# python/Dockerfile, python/pyproject.toml, python/requirements-dev.txt, and
# any .gitkeep. A sorted MANIFEST (excluding itself) is embedded at the zip
# root.
#
# publish creates or updates (idempotent) the GitHub Release for the tag and
# uploads both assets, replacing any existing asset of the same name.
# --dry-run (or RELEASE_DRY_RUN=1) prints the planned API calls without
# making any network call.
#
# Dependencies: git, zip, unzip, sha256sum or shasum, curl.
# Env vars: CIRCLE_TAG (CI tag), GITHUB_RELEASE_TOKEN (fine-grained PAT with
# Contents: RW on darthjee/tingle, required by publish unless --dry-run).

set -euo pipefail

REPO_API="https://api.github.com/repos/darthjee/tingle"
REPO_UPLOADS="https://uploads.github.com/repos/darthjee/tingle"
INCLUDES="bin commands completions shell python node README.md LICENSE"
PRUNE_PATTERN='^python/(tests/|Dockerfile$|pyproject\.toml$|requirements-dev\.txt$)'
GITKEEP_PATTERN='(^|/)\.gitkeep$'
SENSITIVE_PATTERN='(^|/)(\.env|\.netrc|\.npmrc|id_[a-z0-9_]+|.*\.pem|.*\.key|.*\.p12|.*\.pfx)$'

resolve_tag() {
  if [ -n "${CIRCLE_TAG:-}" ]; then
    echo "$CIRCLE_TAG"
  elif [ -n "${1:-}" ]; then
    echo "$1"
  else
    echo "release_cli.sh: no tag (\$CIRCLE_TAG unset and no argument given)" >&2
    exit 1
  fi
}

resolve_files() {
  # shellcheck disable=SC2086
  git ls-files -- $INCLUDES \
    | grep -Ev "$PRUNE_PATTERN" \
    | grep -Ev "$GITKEEP_PATTERN" \
    | LC_ALL=C sort
}

guard_sensitive_files() {
  local files="$1"
  local offenders
  offenders=$(echo "$files" | grep -Ei "$SENSITIVE_PATTERN" || true)

  if [ -n "$offenders" ]; then
    echo "release_cli.sh: refusing to package sensitive-looking files:" >&2
    echo "$offenders" >&2
    exit 1
  fi
}

sha_tool() {
  if command -v sha256sum >/dev/null 2>&1; then
    echo "sha256sum"
  else
    echo "shasum -a 256"
  fi
}

cmd_build() {
  local tag files zip_name zip_path tmp_dir manifest
  tag=$(resolve_tag "${1:-}")
  zip_name="tingle-${tag}.zip"
  zip_path="dist/${zip_name}"

  files=$(resolve_files)
  guard_sensitive_files "$files"

  mkdir -p dist
  rm -f "$zip_path" "${zip_path}.sha256"

  tmp_dir=$(mktemp -d)
  manifest="$tmp_dir/MANIFEST"
  echo "$files" > "$manifest"

  echo "$files" | zip -q "$zip_path" -@
  zip -j -q "$zip_path" "$manifest"
  rm -rf "$tmp_dir"

  (
    cd dist
    # shellcheck disable=SC2046
    $(sha_tool) "$zip_name" > "${zip_name}.sha256"
  )

  echo "Built $zip_path"
}

release_body() {
  local tag="$1"
  cat <<EOF
Download: https://github.com/darthjee/tingle/releases/download/${tag}/tingle-${tag}.zip
Unzip it and run \`bin/tingle install\` to add tingle to your PATH.
EOF
}

api_request() {
  # api_request METHOD URL [DATA]
  local method="$1" url="$2" data="${3:-}"
  local response http_code body

  if [ -n "$data" ]; then
    response=$(curl -sS -w '\n%{http_code}' -X "$method" \
      -H "Authorization: Bearer $GITHUB_RELEASE_TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$url")
  else
    response=$(curl -sS -w '\n%{http_code}' -X "$method" \
      -H "Authorization: Bearer $GITHUB_RELEASE_TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "$url")
  fi

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')

  API_HTTP_CODE="$http_code"
  API_BODY="$body"
}

api_upload() {
  # api_upload URL CONTENT_TYPE FILE
  local url="$1" content_type="$2" file="$3"
  local response http_code body

  response=$(curl -sS -w '\n%{http_code}' -X POST \
    -H "Authorization: Bearer $GITHUB_RELEASE_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -H "Content-Type: $content_type" \
    --data-binary "@${file}" \
    "$url")

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')

  API_HTTP_CODE="$http_code"
  API_BODY="$body"
}

assert_2xx() {
  local context="$1"
  case "$API_HTTP_CODE" in
    2??) ;;
    *)
      echo "release_cli.sh: $context failed (HTTP $API_HTTP_CODE)" >&2
      echo "$API_BODY" >&2
      exit 1
      ;;
  esac
}

json_field() {
  # json_field FIELD <<< JSON — naive single-level string/number extractor
  local field="$1"
  python3 -c "import sys, json; print(json.load(sys.stdin).get(\"$field\", \"\"))"
}

dry_run_call() {
  local method="$1" url="$2" data="${3:-}"
  echo "$method $url"
  echo "  Authorization: Bearer ***"
  if [ -n "$data" ]; then
    echo "  $data"
  fi
}

cmd_publish() {
  local dry_run=0 tag_arg=""
  for arg in "$@"; do
    case "$arg" in
      --dry-run)
        dry_run=1
        ;;
      *)
        tag_arg="$arg"
        ;;
    esac
  done

  if [ "${RELEASE_DRY_RUN:-0}" = "1" ]; then
    dry_run=1
  fi

  if [ "$dry_run" -eq 0 ] && [ -z "${GITHUB_RELEASE_TOKEN:-}" ]; then
    echo "release_cli.sh: GITHUB_RELEASE_TOKEN is not set — add it as a" \
      "CircleCI project env var (Project Settings > Environment Variables)" >&2
    exit 1
  fi

  local tag zip_name sha_name zip_path sha_path
  tag=$(resolve_tag "$tag_arg")
  zip_name="tingle-${tag}.zip"
  sha_name="${zip_name}.sha256"
  zip_path="dist/${zip_name}"
  sha_path="dist/${sha_name}"

  if [ ! -f "$zip_path" ] || [ ! -f "$sha_path" ]; then
    echo "release_cli.sh: $zip_path and/or $sha_path missing — run" \
      "'scripts/release_cli.sh build $tag' first" >&2
    exit 1
  fi

  local body release_id
  body=$(release_body "$tag")
  local escaped_body
  escaped_body=$(python3 -c 'import json, sys; print(json.dumps(sys.stdin.read()))' <<< "$body")

  local release_payload
  release_payload=$(cat <<EOF
{"tag_name":"$tag","name":"$tag","draft":false,"prerelease":false,"generate_release_notes":true,"body":$escaped_body}
EOF
)

  if [ "$dry_run" -eq 1 ]; then
    dry_run_call GET "$REPO_API/releases/tags/$tag"
    dry_run_call POST "$REPO_API/releases" "$release_payload"
    dry_run_call PATCH "$REPO_API/releases/<id>" "$release_payload"
    dry_run_call POST "$REPO_UPLOADS/releases/<id>/assets?name=$zip_name" "<binary: $zip_path>"
    dry_run_call POST "$REPO_UPLOADS/releases/<id>/assets?name=$sha_name" "<binary: $sha_path>"
    return 0
  fi

  api_request GET "$REPO_API/releases/tags/$tag"
  if [ "$API_HTTP_CODE" = "404" ]; then
    api_request POST "$REPO_API/releases" "$release_payload"
    assert_2xx "create release"
    release_id=$(echo "$API_BODY" | json_field id)
  elif [ "$API_HTTP_CODE" = "200" ]; then
    release_id=$(echo "$API_BODY" | json_field id)
    api_request PATCH "$REPO_API/releases/$release_id" "$release_payload"
    assert_2xx "update release"
  else
    assert_2xx "lookup release"
  fi

  upload_asset "$release_id" "$zip_name" "application/zip" "$zip_path"
  upload_asset "$release_id" "$sha_name" "text/plain" "$sha_path"

  echo "Published $tag"
}

upload_asset() {
  local release_id="$1" name="$2" content_type="$3" file="$4"
  local existing_id

  api_request GET "$REPO_API/releases/$release_id/assets"
  assert_2xx "list assets"
  existing_id=$(echo "$API_BODY" | python3 -c "
import sys, json
assets = json.load(sys.stdin)
for asset in assets:
    if asset.get('name') == '$name':
        print(asset['id'])
        break
")

  if [ -n "$existing_id" ]; then
    api_request DELETE "$REPO_API/releases/assets/$existing_id"
    assert_2xx "delete existing asset $name"
  fi

  api_upload "$REPO_UPLOADS/releases/$release_id/assets?name=$name" "$content_type" "$file"
  assert_2xx "upload asset $name"
}

main() {
  local subcommand="${1:-}"
  [ $# -gt 0 ] && shift || true

  case "$subcommand" in
    build)
      cmd_build "$@"
      ;;
    publish)
      cmd_publish "$@"
      ;;
    *)
      echo "Usage: $0 {build|publish} [options]" >&2
      exit 1
      ;;
  esac
}

main "$@"
