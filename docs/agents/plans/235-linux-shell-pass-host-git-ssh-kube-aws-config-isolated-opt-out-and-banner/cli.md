# Cli Plan: linux shell: pass host git/ssh/kube/aws config, --isolated opt-out and banner

Main plan: [plan.md](plan.md)

## Shared contracts

Relies on `shell` for `tingle linux shell [--isolated]`, `TINGLE_LINUX_ISOLATED=1`, the stderr banner, and the list of what the shell brings in: git config (read-only), the SSH agent and ssh config/known_hosts (read-only, never private keys), the kubeconfig (read-write, first `KUBECONFIG` path only), `~/.aws` (read-write), the non-empty `AWS_*` variables, the reset git credential helper, and `--network host` on native Linux Docker.

## Implementation Steps

### Step 1 — Document --isolated and host integration in linux.long_help
In `commands/shell.json`, `linux.long_help`:
- change the usage line to `tingle linux shell [--isolated]`;
- add a short paragraph on what `shell` brings in from the host, each item only when present;
- add an example for `tingle linux shell --isolated`, and mention `TINGLE_LINUX_ISOLATED=1`;
- mention the stderr banner;
- add a pointer to `docs/guides/linux.md` for the full tool list and known limitations.

Keep the existing style (`\n`-escaped text, four-space-indented examples). Leave `short_help` unchanged.

## Files to Change
- `commands/shell.json` — `linux.long_help`.

## Notes
- Check that the JSON is still valid (`python3 -m json.tool commands/shell.json`) and that `tingle help linux` renders it.
- The user guide `docs/guides/linux.md` is updated in part 4 of #231, not here.
