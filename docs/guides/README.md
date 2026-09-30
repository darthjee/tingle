# Tingle User Guides

End-user guides for Tingle, one per `tingle` command. Each guide explains
what the command does, how to run it, and its options, with examples.

For a quick summary of any command, run `tingle --help <command>`.

## Guides

- [`install`](install.md) — Install tingle onto PATH and enable bash completion.
- [`uninstall`](uninstall.md) — Remove tingle's PATH and bash completion wiring from ~/.bashrc.
- [`update`](update.md) — Update tingle: a web install to the latest or a pinned release, or a git checkout with `git pull`.
- [`linux`](linux.md) — GNU/Linux toolbox (sed, shell with git, kubectl, aws, ...) in a container.
- [`kube`](kube.md) — Kubernetes (EKS) subcommand with a scoped alias layer.
- [`code_check`](code_check.md) — Code evaluation checks, grouped as subcommands.
  - [`file_size`](code_check/file_size.md) — Token efficiency triage: file size analysis.
- [`check_file_size`](check_file_size.md) — Deprecated: use `code_check file_size`.
