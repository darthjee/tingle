#!/usr/bin/env bash
#
# release_image.sh — build, smoke-test, and publish the darthjee/tingle and
# darthjee/tingle_rubycritic Docker images, plus update their Docker Hub
# descriptions.
#
# Usage:
#   scripts/release_image.sh setup-builder
#   scripts/release_image.sh build [linux|rubycritic]
#   scripts/release_image.sh smoke-test [linux|rubycritic]
#   scripts/release_image.sh scan [linux|rubycritic]
#   scripts/release_image.sh publish [linux|rubycritic]
#   scripts/release_image.sh update-description [linux|rubycritic]
#
# Image selector: the optional second argument picks the image; it defaults
# to "linux", so calls without a selector behave as before. setup-builder
# ignores it (the builder is shared). An unknown selector prints the usage
# line on stderr and exits 1. Per-image settings (see select_image()):
#
#   Setting            linux                            rubycritic
#   Image name         darthjee/tingle                  darthjee/tingle_rubycritic
#   Dockerfile         shell/linux/Dockerfile           docker/rubycritic/Dockerfile
#   Build context      . (repo root)                    docker/rubycritic
#   Change detection   shell/linux/ since previous tag  none, always runs
#   Smoke test         smoke_test_image                 smoke_test_rubycritic
#   Short description  DOCKERHUB_SHORT_DESCRIPTION.txt  docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt
#   Full description   DOCKERHUB_DESCRIPTION.md         docker/rubycritic/DOCKERHUB_DESCRIPTION.md
#
# Tag resolution (both images): $CIRCLE_TAG when set (CI), else the trimmed
# content of shell/linux/VERSION (local dev). In CI, the pin file must match
# $CIRCLE_TAG exactly or the job hard-fails before building/publishing.
#
# Platforms: $PLATFORMS (space-separated, default "linux/amd64 linux/arm64")
# selects the platforms to build, smoke-test and publish.
#
# setup-builder is idempotent: it creates (if missing) and starts the
# docker-container buildx builder "tingle-builder" and checks its platforms.
# If every platform is already supported it registers and restarts nothing
# (on Docker Desktop no privileged container is run). Otherwise it registers
# QEMU via the pinned tonistiigi/binfmt image only for the missing platforms,
# then stops the builder so BuildKit detects platforms again when it starts;
# if they are still missing, it removes and recreates the builder once as a
# fallback (the only path that loses the builder's cache). Stopping the
# builder interrupts any build using it at that moment.
#
# build loads one local image per platform, tagged <image>:<tag>-<arch>
# (never pushed). publish pushes a single multi-platform <image>:<tag>
# through the same builder (reusing its cache) and fails unless `docker
# buildx imagetools inspect` lists every platform in $PLATFORMS.
#
# Smoke test (linux): runs every check against each local image — GNU sed,
# a non-root user, and every tool in the smoke-check table (one container per
# platform, with --network none) — plus the identity and hardening checks in
# smoke_test_identity(): the image's ENTRYPOINT/CMD and default bash, a
# foreign uid (--user 501:20) resolving as tingle-host with a writable
# HOME=/home/tingle, ~/.ssh, ~/.kube and ~/.config and a working `ssh -G`,
# no nss_wrapper for the default uid, an unchanged read-only /etc/passwd, byte-exact sed stdin/stdout,
# non-zero exit codes passed through, and no setuid/setgid files.
#
# Smoke test (rubycritic): see smoke_test_rubycritic().
#
# Scan: scan runs the pinned Trivy image ($TRIVY_IMAGE) against each local
# <image>:<tag>-<arch> image through the docker socket and prints the
# vulnerability report. It is report-only: findings, and Trivy failures such
# as a DB download error, only print a warning — scan never fails the build.
#
# Change detection (linux only): build, smoke-test, scan and publish are safe
# no-ops (exit 0) when shell/linux/ hasn't changed since the previous X.Y.Z
# tag — see changed_since_previous(). The rubycritic image has NO change
# detection: its build, smoke-test, scan and publish never skip, so
# darthjee/tingle_rubycritic:X.Y.Z always exists for tingle X.Y.Z.
#
# Descriptions: update-description sends the image's one-line summary
# (trimmed, 1-100 characters) as the Docker Hub "description" and its
# markdown file as "full_description", in a single PATCH. It fails when
# either file is missing, the summary is empty or too long, or the
# login/PATCH HTTP call fails.
#
# Dependencies: git, docker, curl, python3.

set -euo pipefail

VERSION_FILE="shell/linux/VERSION"
SHORT_DESCRIPTION_MAX_LENGTH=100
USAGE="Usage: $0 {setup-builder|build|smoke-test|scan|publish|update-description} [linux|rubycritic]"

# Per-image settings, set by select_image().
IMAGE_NAME=""
DOCKERFILE=""
BUILD_CONTEXT=""
SHORT_DESCRIPTION_FILE=""
FULL_DESCRIPTION_FILE=""
CHANGE_DETECTION_PATH=""
SMOKE_TEST_FUNCTION=""
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

usage() {
  echo "$USAGE" >&2
  exit 1
}

# Sets the per-image globals for the given selector. An empty
# CHANGE_DETECTION_PATH disables change detection (the image always builds).
select_image() {
  case "$1" in
    linux)
      IMAGE_NAME="darthjee/tingle"
      DOCKERFILE="shell/linux/Dockerfile"
      BUILD_CONTEXT="."
      SHORT_DESCRIPTION_FILE="DOCKERHUB_SHORT_DESCRIPTION.txt"
      FULL_DESCRIPTION_FILE="DOCKERHUB_DESCRIPTION.md"
      CHANGE_DETECTION_PATH="shell/linux/"
      SMOKE_TEST_FUNCTION="smoke_test_image"
      ;;
    rubycritic)
      IMAGE_NAME="darthjee/tingle_rubycritic"
      DOCKERFILE="docker/rubycritic/Dockerfile"
      BUILD_CONTEXT="docker/rubycritic"
      SHORT_DESCRIPTION_FILE="docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt"
      FULL_DESCRIPTION_FILE="docker/rubycritic/DOCKERHUB_DESCRIPTION.md"
      CHANGE_DETECTION_PATH=""
      SMOKE_TEST_FUNCTION="smoke_test_rubycritic"
      ;;
    *)
      usage
      ;;
  esac
}

previous_tag() {
  git tag --sort=-creatordate | awk 'NR==2{print; exit}'
}

changed_since_previous() {
  if [ -z "$CHANGE_DETECTION_PATH" ]; then
    return 0
  fi

  local prev
  prev=$(previous_tag)

  if [ -z "$prev" ]; then
    return 0
  fi

  ! git diff --quiet "$prev"..HEAD -- "$CHANGE_DETECTION_PATH"
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

create_builder() {
  docker buildx create --name "$BUILDER_NAME" --driver docker-container
}

cmd_setup_builder() {
  if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
    create_builder
  fi

  local missing
  missing=$(missing_platform_archs)

  if [ -n "$missing" ]; then
    echo "Registering QEMU emulation for: $missing"
    docker run --privileged --rm "$BINFMT_IMAGE" --install "$missing"

    # BuildKit only detects emulated platforms when its worker starts, so a
    # builder that was already running must be restarted to see them.
    echo "Restarting builder $BUILDER_NAME to detect new platforms"
    docker buildx stop "$BUILDER_NAME"
    missing=$(missing_platform_archs)

    if [ -n "$missing" ]; then
      echo "Recreating builder $BUILDER_NAME to detect new platforms"
      docker buildx rm "$BUILDER_NAME"
      create_builder
      missing=$(missing_platform_archs)
    fi

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
      -t "$IMAGE_NAME:$tag-$(platform_arch "$platform")" -f "$DOCKERFILE" "$BUILD_CONTEXT"
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

  # Foreign uid: nss_wrapper identity, writable HOME, ~/.ssh, ~/.kube and
  # ~/.config (the host-integration mount parents), working ssh,
  # and a root-owned, read-only, unchanged /etc/passwd.
  # shellcheck disable=SC2016 # expanded inside the container, not here
  "${run[@]}" --user "$FOREIGN_USER" "$image" bash -c '
    platform="$1"
    expected_sha="$2"
    fail() { echo "$1 on $platform (--user '"$FOREIGN_USER"')" >&2; exit 1; }
    [ "$(id -un 2>/dev/null)" = "tingle-host" ] || fail "Foreign uid does not resolve as tingle-host"
    [ "$HOME" = "/home/tingle" ] || fail "HOME is $HOME, not /home/tingle"
    for dir in "$HOME" "$HOME/.ssh" "$HOME/.kube" "$HOME/.config"; do
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

RUBYCRITIC_FIXTURE_DIR="docker/rubycritic/fixture"
RUBYCRITIC_FIXTURE_FILES=(simple.rb complex.rb dup_a.rb dup_b.rb broken.rb empty.rb constants_only.rb)

# Runs the fixture checks from
# docs/agents/specs/code_check/rubycritic/image.md (section 6) against a local
# tingle_rubycritic image, with the canonical run line (--network none,
# read-only /src, foreign uid 501:20): the full fixture run (JSON checked with
# python3), no git in the image, and the empty object on empty stdin. Any
# failure prints "<reason> on <platform>" on stderr and exits 1.
smoke_test_rubycritic() {
  local image="$1"
  local platform="$2"
  local run=(docker run --rm -i --pull never --network none --security-opt no-new-privileges
    --platform "$platform" --user "$FOREIGN_USER"
    -v "$PWD/$RUBYCRITIC_FIXTURE_DIR:/src:ro" -w /src)

  local output status=0
  output=$(printf '%s\n' "${RUBYCRITIC_FIXTURE_FILES[@]}" | "${run[@]}" "$image") || status=$?
  if [ "$status" -ne 0 ]; then
    smoke_fail "Fixture run exited with status $status on $platform"
  fi

  python3 -c '
import json, sys

platform = sys.argv[1]

def fail(reason):
    print(f"{reason} on {platform}", file=sys.stderr)
    sys.exit(1)

try:
    report = json.loads(sys.stdin.read())
except ValueError as error:
    fail(f"Fixture output is not valid JSON ({error})")
if not isinstance(report, dict):
    fail("Fixture output is not a JSON object")

version = ((report.get("metadata") or {}).get("rubycritic") or {}).get("version")
if version != "5.0.0":
    fail(f"metadata.rubycritic.version is {version!r}, not \"5.0.0\"")

modules = {m.get("path"): m for m in report.get("analysed_modules") or []}
expected = {"simple.rb", "complex.rb", "dup_a.rb", "dup_b.rb", "empty.rb", "constants_only.rb"}
if set(modules) != expected:
    fail(f"analysed_modules paths are {sorted(modules)}, expected {sorted(expected)}")

errors = [e.get("path") for e in report.get("parse_errors") or []]
if errors != ["broken.rb"]:
    fail(f"parse_errors paths are {errors}, expected [\"broken.rb\"]")

score = report.get("score")
if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 100:
    fail(f"score is {score!r}, not a number between 0 and 100")

def number(path, key):
    value = modules[path].get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        fail(f"{path} {key} is {value!r}, not a number")
    return value

if not number("simple.rb", "complexity") < 5:
    fail("simple.rb complexity is not below 5")
rating = modules["simple.rb"].get("rating")
if rating != "A":
    fail(f"simple.rb rating is {rating!r}, not \"A\"")
if not number("complex.rb", "complexity") > 50:
    fail("complex.rb complexity is not above 50")
for path in ("dup_a.rb", "dup_b.rb"):
    if not number(path, "duplication") > 0:
        fail(f"{path} duplication is not above 0")
for path in ("empty.rb", "constants_only.rb"):
    if number(path, "complexity") != 0:
        fail(f"{path} complexity is not 0.0")
    if number(path, "methods_count") != 0:
        fail(f"{path} methods_count is not 0")
' "$platform" <<< "$output"

  local git_check
  git_check=$(docker run --rm --network none --platform "$platform" --entrypoint sh "$image" \
    -c 'if command -v git >/dev/null 2>&1; then echo present; else echo absent; fi')
  if [ "$git_check" != "absent" ]; then
    smoke_fail "git is present in the image on $platform"
  fi

  status=0
  output=$("${run[@]}" "$image" < /dev/null) || status=$?
  if [ "$status" -ne 0 ]; then
    smoke_fail "Empty stdin exited with status $status on $platform"
  fi

  python3 -c '
import json, sys

platform = sys.argv[1]
expected = {"metadata": None, "analysed_modules": [], "score": None, "parse_errors": []}
try:
    report = json.loads(sys.stdin.read())
except ValueError:
    report = None
if report != expected:
    print(f"Empty stdin did not print the empty object on {platform}", file=sys.stderr)
    sys.exit(1)
' "$platform" <<< "$output"
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
    "$SMOKE_TEST_FUNCTION" "$IMAGE_NAME:$tag-$(platform_arch "$platform")" "$platform"
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
    -t "$IMAGE_NAME:$tag" -f "$DOCKERFILE" "$BUILD_CONTEXT"

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
  local selector="${2:-linux}"

  case "$subcommand" in
    setup-builder)
      cmd_setup_builder
      ;;
    build)
      select_image "$selector"
      cmd_build
      ;;
    smoke-test)
      select_image "$selector"
      cmd_smoke_test
      ;;
    scan)
      select_image "$selector"
      cmd_scan
      ;;
    publish)
      select_image "$selector"
      cmd_publish
      ;;
    update-description)
      select_image "$selector"
      cmd_update_description
      ;;
    *)
      usage
      ;;
  esac
}

main "$@"
