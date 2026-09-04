#!/usr/bin/env bash
#
# release_image.sh — build, smoke-test, and publish the darthjee/tingle
# Docker image, plus update its Docker Hub description.
#
# Usage:
#   scripts/release_image.sh build
#   scripts/release_image.sh smoke-test
#   scripts/release_image.sh publish
#   scripts/release_image.sh update-description
#
# Tag resolution: $CIRCLE_TAG when set (CI), else the trimmed content of
# shell/linux/VERSION (local dev). In CI, the pin file must match
# $CIRCLE_TAG exactly or the job hard-fails before building/publishing.
#
# Change detection: build and publish are safe no-ops (exit 0) when
# shell/linux/ hasn't changed since the previous v* tag — see
# changed_since_previous().
#
# Dependencies: git, docker, curl, python3.

set -euo pipefail

VERSION_FILE="shell/linux/VERSION"
IMAGE_NAME="darthjee/tingle"

resolve_tag() {
  if [ -n "${CIRCLE_TAG:-}" ]; then
    echo "$CIRCLE_TAG"
  else
    tr -d '[:space:]' < "$VERSION_FILE"
  fi
}

previous_tag() {
  git tag --sort=-creatordate | awk 'NR==2{print; exit}'
}

changed_since_previous() {
  local prev
  prev=$(previous_tag)

  if [ -z "$prev" ]; then
    return 0
  fi

  ! git diff --quiet "$prev"..HEAD -- shell/linux/
}

verify_version_pin() {
  if [ -z "${CIRCLE_TAG:-}" ]; then
    return 0
  fi

  local pinned
  pinned=$(tr -d '[:space:]' < "$VERSION_FILE")

  if [ "$pinned" != "$CIRCLE_TAG" ]; then
    echo "shell/linux/VERSION ($pinned) does not match \$CIRCLE_TAG ($CIRCLE_TAG)" >&2
    exit 1
  fi
}

cmd_build() {
  verify_version_pin

  if ! changed_since_previous; then
    echo "shell/linux/ unchanged since previous release tag — skipping build"
    exit 0
  fi

  local tag
  tag=$(resolve_tag)
  docker build -t "$IMAGE_NAME:$tag" -f shell/linux/Dockerfile .
}

cmd_smoke_test() {
  local tag
  tag=$(resolve_tag)

  docker run --rm "$IMAGE_NAME:$tag" sed --version | grep -qi "GNU sed"

  local uid
  uid=$(docker run --rm "$IMAGE_NAME:$tag" id -u)
  if [ "$uid" = "0" ]; then
    echo "Container runs as root (uid 0)"
    exit 1
  fi
}

cmd_publish() {
  verify_version_pin

  if ! changed_since_previous; then
    echo "shell/linux/ unchanged since previous release tag — skipping publish"
    exit 0
  fi

  local tag
  tag=$(resolve_tag)

  echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin
  docker push "$IMAGE_NAME:$tag"
}

cmd_update_description() {
  local token description
  token=$(curl -s -H "Content-Type: application/json" \
    -X POST \
    -d "{\"username\": \"$DOCKER_HUB_USERNAME\", \"password\": \"$DOCKER_HUB_PASSWORD\"}" \
    https://hub.docker.com/v2/users/login/ | python3 -c 'import sys, json; print(json.load(sys.stdin)["token"])')
  description=$(python3 -c 'import json; print(json.dumps(open("DOCKERHUB_DESCRIPTION.md").read()))')
  curl -s -X PATCH \
    -H "Authorization: JWT $token" \
    -H "Content-Type: application/json" \
    -d "{\"full_description\": $description}" \
    https://hub.docker.com/v2/repositories/darthjee/tingle/
}

main() {
  local subcommand="${1:-}"

  case "$subcommand" in
    build)
      cmd_build
      ;;
    smoke-test)
      cmd_smoke_test
      ;;
    publish)
      cmd_publish
      ;;
    update-description)
      cmd_update_description
      ;;
    *)
      echo "Usage: $0 {build|smoke-test|publish|update-description}" >&2
      exit 1
      ;;
  esac
}

main "$@"
