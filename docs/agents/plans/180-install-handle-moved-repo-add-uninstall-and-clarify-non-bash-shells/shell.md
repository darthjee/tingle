# Shell Plan: install: handle moved repo, add uninstall, and clarify non-bash shells

Main plan: [plan.md](plan.md)

## Shared contracts

- This agent produces the marker-block handling, `shell/uninstall/main.sh` (flow
  verb `run`) and the exact messages listed in
  [plan.md](plan.md#shared-contracts).

## Implementation Steps

### Step 1 — Rewrite a stale marker block in `tingle install`
In `shell/install/executor.sh`:
- When the start marker is present, read the installed path from the block's
  `export PATH="<X>/bin:$PATH"` line.
- Same as `TINGLE_FOLDER`: keep today's "already installed" behavior.
- Different, or the line can't be parsed: rebuild the file with `awk`.
  - Everything outside the markers is copied verbatim.
  - Everything between `# >>> tingle >>>` and `# <<< tingle <<<` (markers
    included) is replaced by a freshly generated block.
  - Write to a temp file (`mktemp`), then `cat tmp > "$BASHRC"` and remove the
    temp file. Writing back through the existing file keeps a symlinked
    `~/.bashrc` (dotfile managers) and its permissions intact; `mv` would not.
  - Print the "updated" message.
- Move the block generation into a small function, shared by the append path
  and the rewrite path, so both emit exactly the same lines.
- Update the header comment: describe the moved-repo behavior and say that
  only bash (`~/.bashrc`) is supported.
- Edge case: a start marker with no end marker. Don't guess. Exit non-zero with
  an error to stderr asking the user to fix `~/.bashrc` by hand.

### Step 2 — Add `tingle uninstall`
Create `shell/uninstall/main.sh`, a copy of `shell/install/main.sh` with
names and comments adapted. Create `shell/uninstall/executor.sh`:
- `TINGLE_FOLDER` is resolved the same way as in install (`$(dirname "$0")/../..`).
- No `~/.bashrc` or no start marker: print "not installed" and exit 0. Don't
  create the file.
- Otherwise, use the same awk + temp-file + `cat >` technique to drop the
  block, markers included.
  - Also drop the single blank line right before the start marker, which
    install added, so repeated install/uninstall cycles don't pile up blank
    lines.
  - Leave all other content untouched.
- Unmatched start marker: same error as in install.
- Never delete the tingle folder. Print the "uninstalled" message with its hint.
- Make both files executable (`chmod +x`), like `shell/install/`.

## Files to Change
- `shell/install/executor.sh` — detect the path, rewrite in place, add the block function, update the header comment.
- `shell/uninstall/main.sh` — new flow-verb dispatcher.
- `shell/uninstall/executor.sh` — new; removes the marker block.

## Notes
- There are no shell tests or shellcheck in CI (CI only lints and tests
  `python/`). Check by hand against a temp `HOME`:
  - `HOME=$(mktemp -d) ./bin/tingle install`, run twice;
  - copy the repo elsewhere and install again, then check the block was rewritten;
  - `tingle uninstall`, run twice;
  - diff `~/.bashrc` before and after around some unrelated content.
- Keep it portable across BSD (macOS) and GNU tools: no `sed -i`, plain POSIX awk.
