# Pre-create mount parents in the image and bump VERSION
When Docker bind-mounts into a directory that doesn't exist, it creates the directory root-owned with mode 755. The container uid then can't create `~/.kube/config.lock`, so `kubectl config use-context` fails, and no tool can write under `~/.config`.

- In `shell/linux/Dockerfile`, in the final root `RUN`, which already creates `/home/tingle/.ssh`, also create `/home/tingle/.kube` and `/home/tingle/.config` and `chmod 1777` them. Update the comment above that step to name all three directories.
- Bump `shell/linux/VERSION` from `0.0.2` to `0.0.3`.
- In `scripts/release_image.sh`, `smoke_test_identity`, foreign-uid case: extend the writability loop (currently `for dir in "$HOME" "$HOME/.ssh"`) to also cover `$HOME/.kube` and `$HOME/.config`. Update the matching header comment near the top of the script.

## Files to Change
- `shell/linux/Dockerfile` — pre-create `.kube` and `.config` with mode 1777.
- `shell/linux/VERSION` — `0.0.3`.
- `scripts/release_image.sh` — smoke test checks that the new directories are writable by a foreign uid.
