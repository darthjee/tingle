# Plan: Install: curl | bash bootstrap and in-zip installer

Issue: [47-install-curl-bash-bootstrap-and-in-zip-installer.md](../../issues/47-install-curl-bash-bootstrap-and-in-zip-installer.md)

## Overview
Adds a new top-level `install/` tree with two scripts: `install/bootstrap.sh`
(fetched fresh from `main` and piped to `bash`) which downloads and unpacks a
published `tingle-<tag>.zip`, then execs `install/installer.sh` (shipped
inside the zip) which copies the unpacked tree to a target directory, writes
a new `tingle.json` manifest, and delegates `.bashrc` wiring to the existing,
unchanged `tingle install` command.

See [shell.md](shell.md) for the full plan.
