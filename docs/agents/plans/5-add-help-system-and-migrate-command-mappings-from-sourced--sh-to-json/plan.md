# Plan: Add help system and migrate command mappings from sourced .sh to JSON

Issue: [5-add-help-system-and-migrate-command-mappings-from-sourced--sh-to-json.md](../issues/5-add-help-system-and-migrate-command-mappings-from-sourced--sh-to-json.md)

## Overview

Add a `--help`/`help` system to `bin/tingle`, backed by a migration of
`commands/*.sh` (sourced shell mappings) to `commands/*.json` (declarative
metadata: path, short_help, long_help), parsed via `jq`.

See [cli.md](cli.md) for the full plan.
