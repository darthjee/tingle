#!/usr/bin/env bash
#
# release_image.sh — build, smoke-test, and publish the darthjee/tingle,
# darthjee/tingle_rubycritic and darthjee/tingle_js_complexity Docker images,
# plus update their Docker Hub descriptions.
#
# Usage:
#   scripts/release_image.sh setup-builder
#   scripts/release_image.sh build [linux|rubycritic|js_complexity]
#   scripts/release_image.sh smoke-test [linux|rubycritic|js_complexity]
#   scripts/release_image.sh scan [linux|rubycritic|js_complexity]
#   scripts/release_image.sh publish [linux|rubycritic|js_complexity]
#   scripts/release_image.sh update-description [linux|rubycritic|js_complexity]
#
# Image selector: the optional second argument picks the image; it defaults
# to "linux", so calls without a selector behave as before. setup-builder
# ignores it (the builder is shared). An unknown selector prints the usage
# line on stderr and exits 1. Per-image settings (see select_image()):
#
#   Setting            linux                            rubycritic                                          js_complexity
#   Image name         darthjee/tingle                  darthjee/tingle_rubycritic                          darthjee/tingle_js_complexity
#   Dockerfile         shell/linux/Dockerfile           docker/rubycritic/Dockerfile                        docker/js_complexity/Dockerfile
#   Build context      . (repo root)                    docker/rubycritic                                   docker/js_complexity
#   Change detection   shell/linux/ since previous tag  none, always runs                                   none, always runs
#   Smoke test         smoke_test_image                 smoke_test_rubycritic                               smoke_test_js_complexity
#   Short description  DOCKERHUB_SHORT_DESCRIPTION.txt  docker/rubycritic/DOCKERHUB_SHORT_DESCRIPTION.txt  docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt
#   Full description   DOCKERHUB_DESCRIPTION.md         docker/rubycritic/DOCKERHUB_DESCRIPTION.md          docker/js_complexity/DOCKERHUB_DESCRIPTION.md
#
# Tag resolution (all images): $CIRCLE_TAG when set (CI), else the trimmed
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
# Smoke test (js_complexity): see smoke_test_js_complexity().
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
# darthjee/tingle_rubycritic:X.Y.Z always exists for tingle X.Y.Z. The
# js_complexity image has NO change detection either: its build, smoke-test,
# scan and publish never skip, so darthjee/tingle_js_complexity:X.Y.Z always
# exists for tingle X.Y.Z.
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
USAGE="Usage: $0 {setup-builder|build|smoke-test|scan|publish|update-description} [linux|rubycritic|js_complexity]"

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
    js_complexity)
      IMAGE_NAME="darthjee/tingle_js_complexity"
      DOCKERFILE="docker/js_complexity/Dockerfile"
      BUILD_CONTEXT="docker/js_complexity"
      SHORT_DESCRIPTION_FILE="docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt"
      FULL_DESCRIPTION_FILE="docker/js_complexity/DOCKERHUB_DESCRIPTION.md"
      CHANGE_DETECTION_PATH=""
      SMOKE_TEST_FUNCTION="smoke_test_js_complexity"
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

# Runs the fixture checks from docs/agents/tingle-rubycritic-image.md
# ("Smoke test") against a local tingle_rubycritic image, with the canonical
# run line (--network none, read-only /src, foreign uid 501:20): the full
# fixture run (JSON checked with python3, "methods" included; the fixture's
# coverage/ holds a leftover .resultset.json.lock, which must neither crash the
# read-only run nor show up in the report), no git in the image, and the empty
# object on empty stdin. Any failure prints "<reason> on <platform>" on stderr and exits 1.
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

coverage_paths = [p for p in list(modules) + errors if str(p).startswith("coverage/")]
if coverage_paths:
    fail(f"report has paths under coverage/: {coverage_paths}")

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

methods = report.get("methods")
if not isinstance(methods, list) or not all(isinstance(m, dict) for m in methods):
    fail(f"methods is {methods!r}, not a list of objects")
complex_run = [m for m in methods if m.get("path") == "complex.rb" and m.get("name") == "Classifier#classify"]
if len(complex_run) != 1:
    fail("methods has no single complex.rb Classifier#classify entry")
complex_score = complex_run[0].get("score")
if isinstance(complex_score, bool) or not isinstance(complex_score, (int, float)) or not complex_score > 50:
    fail(f"complex.rb Classifier#classify score is {complex_score!r}, not a number above 50")
complex_line = complex_run[0].get("line")
if isinstance(complex_line, bool) or not isinstance(complex_line, int):
    fail(f"complex.rb Classifier#classify line is {complex_line!r}, not an int")
for entry in methods:
    entry_path, entry_name = entry.get("path"), str(entry.get("name"))
    if entry_path in ("broken.rb", "empty.rb", "constants_only.rb"):
        fail(f"methods has an entry for {entry_path}")
    if entry_name.endswith("#none"):
        fail(f"methods has the non-method entry {entry_name}")
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
expected = {"metadata": None, "analysed_modules": [], "score": None, "parse_errors": [], "methods": []}
try:
    report = json.loads(sys.stdin.read())
except ValueError:
    report = None
if report != expected:
    print(f"Empty stdin did not print the empty object on {platform}", file=sys.stderr)
    sys.exit(1)
' "$platform" <<< "$output"
}

JS_COMPLEXITY_FIXTURE_DIR="docker/js_complexity/fixture"
JS_COMPLEXITY_FIXTURE_FILES=(simple.js complex.ts component.tsx widget.jsx dup_a.js dup_b.js broken.js
  empty.js short.js bundle.min.js build/out.js ext/a.mjs ext/b.cjs ext/c.mts ext/d.cts ext/UPPER.JS
  ext/types.d.ts crlf.js bom.ts latin1.js Cart.vue NoScript.vue External.vue Coffee.vue TwoBlocks.vue
  Counter.svelte Page.astro Cart.vue.ts)
# Hostile lines piped after the fixture list: an empty line, an absolute path,
# a ".." segment, a duplicate and a missing file. Each must be refused.
JS_COMPLEXITY_HOSTILE_LINES=("" /etc/passwd ../outside.js simple.js missing.js)

# Runs the fixture checks from docs/agents/tingle-js-complexity-image.md
# ("Smoke test") against a local tingle_js_complexity image, with the
# canonical run line (--network none, read-only /src, foreign uid 501:20): the
# fixture list plus the hostile lines on stdin (exit 0, one JSON object checked
# with python3: tool versions, one files[] entry per input line in order, the
# FTA expectations per fixture, the jscpd duplication expectations (the
# dup_a.js/dup_b.js clone, 0 for simple.js and empty.js, null for broken.js,
# latin1.js and the hostile lines, no jscpd warning), the escomplex
# expectations (version 0.1.0, >= 20 functions for complex.ts with "reducer"
# and a "Store." method, [] for empty.js and short.js, null for broken.js,
# latin1.js and the refused lines, every line/cyclo/sloc an int >= 1, no
# path-less escomplex warning), the single-file component expectations (normal
# rows for Cart.vue, TwoBlocks.vue, Counter.svelte, Page.astro and Cart.vue.ts
# with the original line numbers, an empty row for NoScript.vue and
# External.vue, a PARSE row with an entrypoint warning for Coffee.vue), refused
# hostile lines), no git in the image, and empty files/warnings on empty stdin.
# Any failure prints "<reason> on <platform>" on stderr and exits 1.
smoke_test_js_complexity() {
  local image="$1"
  local platform="$2"
  local run=(docker run --rm -i --pull never --network none --security-opt no-new-privileges
    --platform "$platform" --user "$FOREIGN_USER"
    -v "$PWD/$JS_COMPLEXITY_FIXTURE_DIR:/src:ro" -w /src)
  local lines=("${JS_COMPLEXITY_FIXTURE_FILES[@]}" "${JS_COMPLEXITY_HOSTILE_LINES[@]}")

  local output status=0
  output=$(printf '%s\n' "${lines[@]}" | "${run[@]}" "$image") || status=$?
  if [ "$status" -ne 0 ]; then
    smoke_fail "Fixture run exited with status $status on $platform"
  fi

  python3 -c '
import json, sys

platform = sys.argv[1]
lines = sys.argv[2:]

def fail(reason):
    print(f"{reason} on {platform}", file=sys.stderr)
    sys.exit(1)

try:
    report = json.loads(sys.stdin.read())
except ValueError as error:
    fail(f"Fixture output is not valid JSON ({error})")
if not isinstance(report, dict):
    fail("Fixture output is not a JSON object")

versions = report.get("tool_versions") or {}
fta_version = versions.get("fta")
if fta_version != "3.1.0":
    fail(f"tool_versions.fta is {fta_version!r}, not \"3.1.0\"")
jscpd_version = versions.get("jscpd")
if jscpd_version != "5.4.1":
    fail(f"tool_versions.jscpd is {jscpd_version!r}, not \"5.4.1\"")
escomplex_version = versions.get("escomplex")
if escomplex_version != "0.1.0":
    fail(f"tool_versions.escomplex is {escomplex_version!r}, not \"0.1.0\"")

files = report.get("files")
if not isinstance(files, list) or not all(isinstance(f, dict) for f in files):
    fail(f"files is {files!r}, not a list of objects")
paths = [f.get("path") for f in files]
if paths != lines:
    fail(f"files paths are {paths}, expected the input lines {lines}")

warnings = report.get("warnings")
if not isinstance(warnings, list) or not all(isinstance(w, dict) for w in warnings):
    fail(f"warnings is {warnings!r}, not a list of objects")

hostile = {
    "": "empty line",
    "/etc/passwd": "absolute path",
    "../outside.js": "path has a \x27..\x27 segment",
    "simple.js": "duplicate line",
    "missing.js": "not a regular file under /src",
}

def warnings_for(path):
    return [(w.get("tool"), w.get("message")) for w in warnings if w.get("path") == path]

# Warnings for a fixture path, without the one its hostile duplicate line gets.
def fixture_warnings_for(path):
    hostile_warning = ("entrypoint", hostile.get(path))
    return [w for w in warnings_for(path) if w != hostile_warning]

# The fixture rows come first, so the first entry for a path is its fixture row.
entries = {}
for entry in files:
    entries.setdefault(entry["path"], entry)

def normal(path):
    entry = entries[path]
    flag = entry.get("parse_error")
    if flag is not False:
        fail(f"{path} parse_error is {flag!r}, not false")
    fta = entry.get("fta")
    if not isinstance(fta, dict):
        fail(f"{path} fta is {fta!r}, not an object")
    score = fta.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        fail(f"{path} fta.score is {score!r}, not a number")
    if fixture_warnings_for(path):
        fail(f"{path} has warnings {fixture_warnings_for(path)}")
    return fta

def parse_error(path, message=None):
    entry = entries[path]
    flag, fta = entry.get("parse_error"), entry.get("fta")
    if flag is not True:
        fail(f"{path} parse_error is {flag!r}, not true")
    if fta is not None:
        fail(f"{path} fta is {fta!r}, not null")
    fta_warnings = [m for tool, m in warnings_for(path) if tool == "fta"]
    if not fta_warnings:
        fail(f"{path} has no fta warning")
    if message is not None and message not in fta_warnings:
        fail(f"{path} fta warnings are {fta_warnings}, expected {message!r}")

def refused(entry, message):
    path, flag, fta = entry.get("path"), entry.get("parse_error"), entry.get("fta")
    if flag is not False:
        fail(f"refused line {path!r} parse_error is {flag!r}, not false")
    if fta is not None:
        fail(f"refused line {path!r} fta is {fta!r}, not null")
    if ("entrypoint", message) not in warnings_for(path):
        fail(f"refused line {path!r} has no entrypoint warning {message!r}")

simple = normal("simple.js")
if not simple["score"] < 20 or simple.get("assessment") != "OK":
    fail(f"simple.js fta is {simple}, expected score < 20 and \"OK\"")
complex_fta = normal("complex.ts")
if not complex_fta["score"] > 60 or complex_fta.get("assessment") != "Needs improvement":
    fail(f"complex.ts fta is {complex_fta}, expected score > 60 and \"Needs improvement\"")
for path in ("component.tsx", "widget.jsx", "dup_a.js", "dup_b.js", "build/out.js",
             "ext/a.mjs", "ext/b.cjs", "ext/c.mts", "ext/d.cts", "ext/UPPER.JS", "ext/types.d.ts"):
    normal(path)
parse_error("broken.js")
empty = entries["empty.js"]
if empty.get("parse_error") is not False or empty.get("fta") is not None:
    fail(f"empty.js is {empty}, expected parse_error false and fta null")
for path in ("short.js", "bundle.min.js"):
    line_count = normal(path).get("lines")
    if line_count != 1:
        fail(f"{path} fta.lines is {line_count!r}, not 1")
if normal("crlf.js")["score"] != normal("ext/a.mjs")["score"]:
    fail("crlf.js score differs from ext/a.mjs")
if normal("bom.ts")["score"] != normal("ext/c.mts")["score"]:
    fail("bom.ts score differs from ext/c.mts")
parse_error("latin1.js", "file is not valid UTF-8")

# Single-file components ("Smoke test").
cart = normal("Cart.vue")
if not 25 <= cart["score"] <= 40 or cart.get("lines") != 12:
    fail(f"Cart.vue fta is {cart}, expected 25 <= score <= 40 and lines 12")
for path in ("TwoBlocks.vue", "Counter.svelte", "Page.astro"):
    normal(path)
if normal("Cart.vue.ts") == cart:
    fail("Cart.vue.ts has the same fta row as Cart.vue")
for path in ("NoScript.vue", "External.vue"):
    entry = entries[path]
    if entry.get("parse_error") is not False or entry.get("fta") is not None:
        fail(f"{path} is {entry}, expected parse_error false and fta null")
    if warnings_for(path):
        fail(f"{path} has warnings {warnings_for(path)}")
coffee = entries["Coffee.vue"]
if coffee.get("parse_error") is not True or coffee.get("fta") is not None:
    fail(f"Coffee.vue is {coffee}, expected parse_error true and fta null")
coffee_warning = ("entrypoint", "unsupported <script lang=\"coffee\">")
coffee_warnings = warnings_for("Coffee.vue")
if coffee_warnings != [coffee_warning]:
    fail(f"Coffee.vue warnings are {coffee_warnings}, expected [{coffee_warning}]")

jscpd_warnings = [w for w in warnings if w.get("tool") == "jscpd"]
if jscpd_warnings:
    fail(f"jscpd warnings {jscpd_warnings}")

def duplicated_lines(path):
    duplication = entries[path].get("duplication")
    lines_count = duplication.get("lines") if isinstance(duplication, dict) else None
    if isinstance(lines_count, bool) or not isinstance(lines_count, int):
        fail(f"{path} duplication is {duplication!r}, not {{\"lines\": <int>}}")
    return lines_count

for path in ("dup_a.js", "dup_b.js"):
    if not duplicated_lines(path) >= 20:
        fail(f"{path} duplication.lines is {duplicated_lines(path)}, not >= 20")
for path in ("simple.js", "empty.js", "Cart.vue", "NoScript.vue", "External.vue", "TwoBlocks.vue",
             "Counter.svelte", "Page.astro", "Cart.vue.ts"):
    if duplicated_lines(path) != 0:
        fail(f"{path} duplication.lines is {duplicated_lines(path)}, not 0")
for path in ("broken.js", "latin1.js", "Coffee.vue"):
    duplication = entries[path].get("duplication")
    if duplication is not None:
        fail(f"{path} duplication is {duplication!r}, not null")

fixture_count = len(lines) - len(hostile)
for entry in files[fixture_count:]:
    refused(entry, hostile[entry["path"]])
    path, duplication = entry.get("path"), entry.get("duplication")
    if duplication is not None:
        fail(f"refused line {path!r} duplication is {duplication!r}, not null")
    functions = entry.get("functions")
    if functions is not None:
        fail(f"refused line {path!r} functions is {functions!r}, not null")

escomplex_wrapper_warnings = [w for w in warnings if w.get("tool") == "escomplex" and "path" not in w]
if escomplex_wrapper_warnings:
    fail(f"escomplex wrapper warnings {escomplex_wrapper_warnings}")

def is_positive_int(value):
    return not isinstance(value, bool) and isinstance(value, int) and value >= 1

for entry in files:
    path, functions = entry.get("path"), entry.get("functions")
    if functions is None:
        continue
    if not isinstance(functions, list):
        fail(f"{path} functions is {functions!r}, not a list or null")
    for function in functions:
        if not isinstance(function, dict) or not isinstance(function.get("name"), str):
            fail(f"{path} has a malformed function {function!r}")
        for key in ("line", "cyclo", "sloc"):
            if not is_positive_int(function.get(key)):
                fail(f"{path} function {function!r} {key} is not an int >= 1")

def functions_of(path):
    functions = entries[path].get("functions")
    if not isinstance(functions, list):
        fail(f"{path} functions is {functions!r}, not a list")
    return functions

complex_names = [f["name"] for f in functions_of("complex.ts")]
if len(complex_names) < 20:
    fail(f"complex.ts has {len(complex_names)} functions, not >= 20")
if "reducer" not in complex_names:
    fail(f"complex.ts functions {complex_names} have no \"reducer\"")
if not any(name.startswith("Store.") for name in complex_names):
    fail(f"complex.ts functions {complex_names} have no \"Store.\" method")
for path in ("empty.js", "short.js", "NoScript.vue", "External.vue"):
    if functions_of(path) != []:
        fail(f"{path} functions is {functions_of(path)!r}, not []")
for path in ("broken.js", "latin1.js", "Coffee.vue"):
    functions = entries[path].get("functions")
    if functions is not None:
        fail(f"{path} functions is {functions!r}, not null")

# Function lines of the components are their original lines.
def function_lines(path):
    return {f["name"]: f["line"] for f in functions_of(path)}

expected_lines = {
    "Cart.vue": {"<anon method-1>": 13},
    "TwoBlocks.vue": {"normaliseTag": 8, "label": 17},
    "Counter.svelte": {"instanceCount": 4, "increment": 16},
    "Page.astro": {"publishedSlugs": 5, "toggleTheme": 17},
}
for path, expected in expected_lines.items():
    actual = function_lines(path)
    if any(actual.get(name) != line for name, line in expected.items()):
        fail(f"{path} function lines are {actual}, expected {expected}")
cart_functions = functions_of("Cart.vue")
if len(cart_functions) != 1:
    fail(f"Cart.vue functions are {cart_functions}, expected exactly one")
' "$platform" "${lines[@]}" <<< "$output"

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
try:
    report = json.loads(sys.stdin.read())
except ValueError:
    report = None
if not isinstance(report, dict) or report.get("files") != [] or report.get("warnings") != []:
    print(f"Empty stdin did not print empty files and warnings on {platform}", file=sys.stderr)
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
