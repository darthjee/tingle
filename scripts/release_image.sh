#!/usr/bin/env bash
#
# release_image.sh — build, smoke-test, and publish the darthjee/tingle
# Docker image, plus update its Docker Hub description.
#
# Usage:
#   scripts/release_image.sh setup-builder
#   scripts/release_image.sh build
#   scripts/release_image.sh smoke-test
#   scripts/release_image.sh publish
#   scripts/release_image.sh update-description
#
# Tag resolution: $CIRCLE_TAG when set (CI), else the trimmed content of
# shell/linux/VERSION (local dev). In CI, the pin file must match
# $CIRCLE_TAG exactly or the job hard-fails before building/publishing.
#
# Platforms: $PLATFORMS (space-separated, default "linux/amd64 linux/arm64")
# selects the platforms to build, smoke-test and publish.
#
# setup-builder is idempotent: it creates (if missing) and bootstraps the
# docker-container buildx builder "tingle-builder", and registers QEMU via
# the pinned tonistiigi/binfmt image only for platforms the builder does not
# already support (on Docker Desktop no privileged container is run).
#
# Change detection: build and publish are safe no-ops (exit 0) when
# shell/linux/ hasn't changed since the previous X.Y.Z tag — see
# changed_since_previous().
#
# Descriptions: update-description sends the one-line summary in
# DOCKERHUB_SHORT_DESCRIPTION.txt (trimmed, 1-100 characters) as the Docker
# Hub "description" and DOCKERHUB_DESCRIPTION.md as "full_description", in
# a single PATCH. It fails when either file is missing, the summary is
# empty or too long, or the login/PATCH HTTP call fails.
#
# Dependencies: git, docker, curl, python3.

set -euo pipefail

VERSION_FILE="shell/linux/VERSION"
IMAGE_NAME="darthjee/tingle"
SHORT_DESCRIPTION_FILE="DOCKERHUB_SHORT_DESCRIPTION.txt"
FULL_DESCRIPTION_FILE="DOCKERHUB_DESCRIPTION.md"
SHORT_DESCRIPTION_MAX_LENGTH=100
PLATFORMS="${PLATFORMS:-linux/amd64 linux/arm64}"
BUILDER_NAME="tingle-builder"
BINFMT_IMAGE="tonistiigi/binfmt:qemu-v10.2.3"

resolve_tag() {
  if [ -n "${CIRCLE_TAG:-}" ]; then
    echo "$CIRCLE_TAG"
  else
    tr -d '[:space:]' < "$VERSION_FILE"
  fi
}

platform_arch() {
  echo "${1#linux/}"
}

platforms_csv() {
  local csv=""
  local platform
  for platform in $PLATFORMS; do
    csv="${csv:+$csv,}$platform"
  done
  echo "$csv"
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

builder_platforms() {
  docker buildx inspect --bootstrap "$BUILDER_NAME" | awk -F': *' '/^Platforms:/{print $2; exit}'
}

missing_platform_archs() {
  local supported
  supported=$(builder_platforms)

  local missing=""
  local platform
  for platform in $PLATFORMS; do
    case ",${supported// /}," in
      *",$platform,"*|*",$platform*,"*) ;;
      *) missing="${missing:+$missing,}$(platform_arch "$platform")" ;;
    esac
  done
  echo "$missing"
}

cmd_setup_builder() {
  if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
    docker buildx create --name "$BUILDER_NAME" --driver docker-container
  fi

  local missing
  missing=$(missing_platform_archs)

  if [ -n "$missing" ]; then
    echo "Registering QEMU emulation for: $missing"
    docker run --privileged --rm "$BINFMT_IMAGE" --install "$missing"

    missing=$(missing_platform_archs)
    if [ -n "$missing" ]; then
      echo "Builder $BUILDER_NAME still does not support: $missing" >&2
      exit 1
    fi
  fi

  echo "Builder $BUILDER_NAME ready for: $(platforms_csv)"
}

cmd_build() {
  if ! changed_since_previous; then
    echo "shell/linux/ unchanged since previous release tag — skipping build"
    exit 0
  fi

  verify_version_pin

  local tag
  tag=$(resolve_tag)
  docker build -t "$IMAGE_NAME:$tag" -f shell/linux/Dockerfile .
}

cmd_smoke_test() {
  if ! changed_since_previous; then
    echo "shell/linux/ unchanged since previous release tag — skipping smoke test"
    exit 0
  fi

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
  if ! changed_since_previous; then
    echo "shell/linux/ unchanged since previous release tag — skipping publish"
    exit 0
  fi

  verify_version_pin

  local tag
  tag=$(resolve_tag)

  echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin
  docker push "$IMAGE_NAME:$tag"
}

cmd_update_description() {
  if [ ! -f "$SHORT_DESCRIPTION_FILE" ]; then
    echo "Missing short description file: $SHORT_DESCRIPTION_FILE" >&2
    exit 1
  fi

  if [ ! -f "$FULL_DESCRIPTION_FILE" ]; then
    echo "Missing full description file: $FULL_DESCRIPTION_FILE" >&2
    exit 1
  fi

  local short_description
  short_description=$(python3 -c 'import sys; print(open(sys.argv[1]).read().strip())' "$SHORT_DESCRIPTION_FILE")

  if [ -z "$short_description" ]; then
    echo "Short description in $SHORT_DESCRIPTION_FILE is empty" >&2
    exit 1
  fi

  local short_length
  short_length=$(printf '%s' "$short_description" | python3 -c 'import sys; print(len(sys.stdin.read()))')

  if [ "$short_length" -gt "$SHORT_DESCRIPTION_MAX_LENGTH" ]; then
    echo "Short description in $SHORT_DESCRIPTION_FILE is $short_length characters (max $SHORT_DESCRIPTION_MAX_LENGTH)" >&2
    exit 1
  fi

  local body
  body=$(python3 -c '
import json, sys
print(json.dumps({
    "description": sys.argv[1],
    "full_description": open(sys.argv[2]).read(),
}))
' "$short_description" "$FULL_DESCRIPTION_FILE")

  local token
  token=$(curl -fsS -H "Content-Type: application/json" \
    -X POST \
    -d "{\"username\": \"$DOCKER_HUB_USERNAME\", \"password\": \"$DOCKER_HUB_PASSWORD\"}" \
    https://hub.docker.com/v2/users/login/ | python3 -c 'import sys, json; print(json.load(sys.stdin)["token"])')

  curl -fsS -X PATCH \
    -H "Authorization: JWT $token" \
    -H "Content-Type: application/json" \
    -d "$body" \
    -o /dev/null \
    "https://hub.docker.com/v2/repositories/$IMAGE_NAME/"

  echo "Updated Docker Hub description for $IMAGE_NAME"
}

main() {
  local subcommand="${1:-}"

  case "$subcommand" in
    setup-builder)
      cmd_setup_builder
      ;;
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
      echo "Usage: $0 {setup-builder|build|smoke-test|publish|update-description}" >&2
      exit 1
      ;;
  esac
}

main "$@"
