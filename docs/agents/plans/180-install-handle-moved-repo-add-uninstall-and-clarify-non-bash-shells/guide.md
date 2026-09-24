# Guide Plan: install: handle moved repo, add uninstall, and clarify non-bash shells

Main plan: [plan.md](plan.md)

## Shared contracts

- Document the behavior and messages exactly as in
  [plan.md](plan.md#shared-contracts), with `/home/you` as the example home.

## Implementation Steps

### Step 1 — Update `docs/guides/install.md`
- Add a "Supported shells" section:
  - bash only (`~/.bashrc`); zsh (the macOS default) and fish are not wired
    and users must add PATH themselves;
  - macOS caveat: Terminal starts bash as a login shell, which reads
    `~/.bash_profile`. Show the one-line `source ~/.bashrc` users add there.
- Rewrite "Running it again":
  - same path: unchanged, "already installed";
  - moved or reinstalled elsewhere: the block is rewritten in place, with the
    new message;
  - the rest of `~/.bashrc` is still never touched.
- Adjust "What it changes" so it no longer says existing content is never
  rewritten. Only the tingle block itself can be rewritten.
- Add a short "Uninstalling" pointer to `uninstall.md`.

### Step 2 — Add `docs/guides/uninstall.md` and list it in the index
- New guide, same structure as `install.md`:
  - what it does;
  - usage (`tingle uninstall`, no options);
  - what it changes (removes the block and markers);
  - running it again (the "not installed" message);
  - the tingle folder is left in place: for example `rm -rf ~/.tingle` for
    web installs, or delete your clone;
  - how to check it worked (open a new shell, `command -v tingle` prints nothing).
- Add `uninstall` to `docs/guides/README.md`, using the short help from
  `commands/shell.json`.
- Update the `install` line's description if its `short_help` changes (it doesn't in this plan).

## Files to Change
- `docs/guides/install.md` — supported shells, moved-repo behavior, uninstall pointer.
- `docs/guides/uninstall.md` — new guide.
- `docs/guides/README.md` — add the `uninstall` entry.

## Notes
- Copy the messages word for word from the final `shell/` scripts. If the
  shell agent's wording differs from the contract, the scripts win.
- Root `README.md` (architect-owned) mentions `tingle install` at line ~103.
  The architect should add a one-line mention of `tingle uninstall` there
  when implementing this issue.
