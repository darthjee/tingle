#!/usr/bin/env bash
#
# release_image.sh — build, smoke-test, and publish the darthjee/tingle
# Docker image, plus update its Docker Hub description.
#
# Usage:
#   scripts/release_image.sh setup-builder
#   scripts/release_image.sh build
#   scripts/release_image.sh smoke-test
#   scripts/release_image.sh scan
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
# build loads one local image per platform, tagged darthjee/tingle:<tag>-<arch>
# (never pushed); smoke-test runs every check against each of them — GNU sed,
# a non-root user, and every tool in the smoke-check table (one container per
# platform, with --network none) — plus the identity and hardening checks in
# smoke_test_identity(): the image's ENTRYPOINT/CMD and default bash, a
# foreign uid (--user 501:20) resolving as tingle-host with a writable
# HOME=/home/tingle and ~/.ssh and a working `ssh -G`, no nss_wrapper for the
# default uid, an unchanged read-only /etc/passwd, byte-exact sed stdin/stdout,
# non-zero exit codes passed through, and no setuid/setgid files. publish
# pushes a single multi-platform darthjee/tingle:<tag> through the same
# builder (reusing its cache) and fails unless `docker buildx imagetools
# inspect` lists every platform in $PLATFORMS.
#
# Scan: scan runs the pinned Trivy image ($TRIVY_IMAGE) against each local
# darthjee/tingle:<tag>-<arch> image through the docker socket and prints the
# vulnerability report. It is report-only: findings, and Trivy failures such
# as a DB download error, only print a warning — scan never fails the build.
#
# Change detection: build, smoke-test, scan and publish are safe no-ops (exit 0) when
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
TRIVY_IMAGE="aquasec/trivy:0.74.0@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969"

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

  local platform
  for platform in $PLATFORMS; do
    echo "Building $IMAGE_NAME:$tag-$(platform_arch "$platform") for $platform"
    docker buildx build --builder "$BUILDER_NAME" --platform "$platform" --load \
      -t "$IMAGE_NAME:$tag-$(platform_arch "$platform")" -f shell/linux/Dockerfile .
  done
}

smoke_test_image() {
  local image="$1"
  local platform="$2"

  docker run --rm --platform "$platform" "$image" sed --version | grep -qi "GNU sed"

  local uid
  uid=$(docker run --rm --platform "$platform" "$image" id -u)
  if [ "$uid" = "0" ]; then
    echo "Container runs as root (uid 0) on $platform" >&2
    exit 1
  fi

  smoke_test_tools "$image" "$platform"
  smoke_test_identity "$image" "$platform"
}

# Smoke-check table: one "name|command" entry per tool. Each command must
# succeed as the tingle user with no network access; its output is discarded.
TOOL_CHECKS=(
  "git|git --version"
  "ssh|ssh -V"
  "less|less --version"
  "jq|jq --version"
  "curl|curl --version"
  "wget|wget --version"
  "dig|dig -v"
  "ping|ping -V"
  "nc|command -v nc"
  "ip|ip -V"
  "vim|vim --version"
  "rg|rg --version"
  "fd|fd --version"
  "bat|bat --version"
  "bash-completion|test -f /usr/share/bash-completion/bash_completion"
  "tree|tree --version"
  "file|file --version"
  "unzip|unzip -v"
  "zip|zip -v"
  "xz|xz --version"
  "bc|bc --version"
  "make|make --version"
  "shellcheck|shellcheck --version"
  "rsync|rsync --version"
  "ps|ps --version"
  "tmux|tmux -V"
  "htop|htop --version"
  "kubectl|kubectl version --client"
  "aws|aws --version"
  "ca bundle|test -s /etc/ssl/certs/ca-certificates.crt"
)

# Runs every TOOL_CHECKS entry inside a single container (runs are slow under
# QEMU) and fails on the first missing or broken tool.
smoke_test_tools() {
  local image="$1"
  local platform="$2"

  # shellcheck disable=SC2016 # expanded inside the container, not here
  docker run --rm --network none --platform "$platform" "$image" bash -c '
    platform="$1"
    shift
    for check in "$@"; do
      name="${check%%|*}"
      command="${check#*|}"
      if ! bash -c "$command" >/dev/null 2>&1; then
        echo "Missing or broken tool on $platform: $name" >&2
        exit 1
      fi
    done
  ' _ "$platform" "${TOOL_CHECKS[@]}"
}

ENTRYPOINT_PATH="/usr/local/bin/tingle-entrypoint"
FOREIGN_USER="501:20"

smoke_fail() {
  echo "$1" >&2
  exit 1
}

# Checks the entrypoint's identity handling and the image hardening. Checks
# are grouped into as few containers as possible (runs are slow under QEMU),
# all with --network none.
smoke_test_identity() {
  local image="$1"
  local platform="$2"
  local run=(docker run --rm --network none --platform "$platform")

  local config
  config=$(docker image inspect --format '{{json .Config.Entrypoint}} {{json .Config.Cmd}}' "$image")
  if [ "$config" != "[\"$ENTRYPOINT_PATH\"] [\"bash\"]" ]; then
    smoke_fail "Unexpected ENTRYPOINT/CMD on $platform: $config"
  fi

  local output
  output=$(echo 'echo ok' | "${run[@]}" -i "$image")
  if [ "$output" != "ok" ]; then
    smoke_fail "Default command is not bash on $platform (got: $output)"
  fi

  # Default uid: no nss_wrapper, the tingle user, and no setuid/setgid files.
  # Prints the sha256 of /etc/passwd for the foreign-uid comparison below.
  local passwd_sha
  # shellcheck disable=SC2016 # expanded inside the container, not here
  passwd_sha=$("${run[@]}" "$image" bash -c '
    platform="$1"
    fail() { echo "$1 on $platform" >&2; exit 1; }
    [ -z "${LD_PRELOAD:-}" ] || fail "LD_PRELOAD is set for the default uid ($LD_PRELOAD)"
    [ "$(id -un)" = "tingle" ] || fail "Default uid does not resolve as tingle"
    suid=$(find / -xdev -perm /6000 -type f 2>/dev/null)
    [ -z "$suid" ] || fail "setuid/setgid files found: $suid"
    sha256sum /etc/passwd | cut -d " " -f 1
  ' _ "$platform")

  # Foreign uid: nss_wrapper identity, writable HOME and ~/.ssh, working ssh,
  # and a root-owned, read-only, unchanged /etc/passwd.
  # shellcheck disable=SC2016 # expanded inside the container, not here
  "${run[@]}" --user "$FOREIGN_USER" "$image" bash -c '
    platform="$1"
    expected_sha="$2"
    fail() { echo "$1 on $platform (--user '"$FOREIGN_USER"')" >&2; exit 1; }
    [ "$(id -un 2>/dev/null)" = "tingle-host" ] || fail "Foreign uid does not resolve as tingle-host"
    [ "$HOME" = "/home/tingle" ] || fail "HOME is $HOME, not /home/tingle"
    for dir in "$HOME" "$HOME/.ssh"; do
      probe="$dir/.smoke-test-$$"
      { touch "$probe" && rm "$probe"; } 2>/dev/null || fail "$dir is not writable"
    done
    ssh -G localhost >/dev/null 2>&1 || fail "ssh -G localhost failed"
    [ "$(stat -c %u /etc/passwd)" = "0" ] || fail "/etc/passwd is not owned by root"
    [ ! -w /etc/passwd ] || fail "/etc/passwd is writable"
    [ "$(sha256sum /etc/passwd | cut -d " " -f 1)" = "$expected_sha" ] || fail "/etc/passwd changed"
  ' _ "$platform" "$passwd_sha"

  # The trailing "." keeps any extra trailing newline from being stripped.
  output=$(printf a | "${run[@]}" -i "$image" sed s/a/b/; echo .)
  if [ "$output" != "b." ]; then
    smoke_fail "sed through the entrypoint printed '$output' instead of 'b' on $platform"
  fi

  if "${run[@]}" "$image" false; then
    smoke_fail "Non-zero exit code was not passed through on $platform"
  fi
}

cmd_smoke_test() {
  if ! changed_since_previous; then
    echo "shell/linux/ unchanged since previous release tag — skipping smoke test"
    exit 0
  fi

  local tag
  tag=$(resolve_tag)

  local platform
  for platform in $PLATFORMS; do
    echo "Smoke-testing $IMAGE_NAME:$tag-$(platform_arch "$platform") on $platform"
    smoke_test_image "$IMAGE_NAME:$tag-$(platform_arch "$platform")" "$platform"
  done
}

cmd_scan() {
  if ! changed_since_previous; then
    echo "shell/linux/ unchanged since previous release tag — skipping scan"
    exit 0
  fi

  local tag
  tag=$(resolve_tag)

  local platform image
  for platform in $PLATFORMS; do
    image="$IMAGE_NAME:$tag-$(platform_arch "$platform")"
    echo "Scanning $image on $platform"
    if ! docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      "$TRIVY_IMAGE" image --platform "$platform" --exit-code 0 --no-progress \
      "$image"; then
      echo "Trivy scan failed for $image on $platform — continuing (report-only)" >&2
    fi
  done
}

verify_published_platforms() {
  local image="$1"

  local manifest
  manifest=$(docker buildx imagetools inspect "$image")

  local platform
  for platform in $PLATFORMS; do
    if ! grep -Eq "Platform:[[:space:]]+${platform}\$" <<< "$manifest"; then
      echo "Published $image is missing platform $platform" >&2
      exit 1
    fi
  done

  echo "Published $image for: $(platforms_csv)"
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

  docker buildx build --builder "$BUILDER_NAME" --platform "$(platforms_csv)" --push \
    -t "$IMAGE_NAME:$tag" -f shell/linux/Dockerfile .

  verify_published_platforms "$IMAGE_NAME:$tag"
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
    scan)
      cmd_scan
      ;;
    publish)
      cmd_publish
      ;;
    update-description)
      cmd_update_description
      ;;
    *)
      echo "Usage: $0 {setup-builder|build|smoke-test|scan|publish|update-description}" >&2
      exit 1
      ;;
  esac
}

main "$@"
