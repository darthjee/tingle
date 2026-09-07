#!/usr/bin/env bash
#
# bump-version.sh — bump the repo's release version across the three places
# that must stay in sync:
#   - README.md               (Current Version / Next Release lines)
#   - install/bootstrap.sh    (pinned TINGLE_VERSION default)
#   - shell/linux/VERSION     (Docker image tag pin)
#
# Usage:
#   scripts/bump-version.sh [X.Y.Z]
#
# With no argument, the new version defaults to README's current
# "Next Release" value. Plain semver only (X.Y.Z, no "v" prefix, no
# pre-release suffix), matching install/bootstrap.sh's documented contract.
#
# This script only edits files — it does not git add/commit/tag anything.
#
# Dependencies: git, sed.

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
README="$ROOT/README.md"
BOOTSTRAP="$ROOT/install/bootstrap.sh"
VERSION_FILE="$ROOT/shell/linux/VERSION"

# Extract current Next Release version from README
current_next=$(grep -oE '\*\*Next Release:\*\* \[[0-9]+\.[0-9]+\.[0-9]+' "$README" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')

if [ $# -ge 1 ]; then
  new_version="$1"
else
  new_version="$current_next"
fi

# Validate semver format
if ! echo "$new_version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "Error: version must be in X.Y.Z format" >&2
  exit 1
fi

# Compute next release (increment patch)
IFS='.' read -r major minor patch <<< "$new_version"
next_release="${major}.${minor}.$((patch + 1))"

echo "New version:  $new_version"
echo "Next release: $next_release"

# Update README Current Version line
sed -i '' \
  "s|\*\*Current Version:\*\* \[[0-9.]*\](https://github.com/darthjee/tingle/releases/tag/[0-9.]*)|\*\*Current Version:\*\* [${new_version}](https://github.com/darthjee/tingle/releases/tag/${new_version})|" \
  "$README"

# Update README Next Release line
sed -i '' \
  "s|\*\*Next Release:\*\* \[[0-9.]*\](https://github.com/darthjee/tingle/compare/[0-9.]*\.\.\.main)|\*\*Next Release:\*\* [${next_release}](https://github.com/darthjee/tingle/compare/${new_version}...main)|" \
  "$README"

# Update install/bootstrap.sh pinned default
sed -i '' \
  "s|VERSION=\"\${TINGLE_VERSION:-[0-9.]*}\"|VERSION=\"\${TINGLE_VERSION:-${new_version}}\"|" \
  "$BOOTSTRAP"

# Update shell/linux/VERSION
printf '%s\n' "$new_version" > "$VERSION_FILE"

echo "Done."
