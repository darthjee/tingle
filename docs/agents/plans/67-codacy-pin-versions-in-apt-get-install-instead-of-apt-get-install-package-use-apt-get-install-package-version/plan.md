# Plan: Codacy: Pin versions in apt get install. Instead of `apt-get install <package>` use `apt-get install <package>=<version>`

Issue: [67-codacy-pin-versions-in-apt-get-install-instead-of-apt-get-install-package-use-apt-get-install-package-version.md](../../issues/67-codacy-pin-versions-in-apt-get-install-instead-of-apt-get-install-package-use-apt-get-install-package-version.md)

## Overview
Pin every package installed by `shell/linux/Dockerfile`'s `apt-get install` call to an explicit version, clearing the Codacy/Hadolint `DL3008` finding.

See [shell.md](shell.md) for the full plan.
