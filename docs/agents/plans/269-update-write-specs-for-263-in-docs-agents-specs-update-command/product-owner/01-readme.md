# Write the shared-contracts README
Create `docs/agents/specs/update_command/README.md`, which holds everything
more than one sub-issue depends on. Start with `Parent issue: #263.` and the
rule that this file wins over a feature spec if they disagree. Sections:

1. **Overview:** what `tingle update` is (a thin command that hands off to
   the incoming release's `install/installer.sh` in update mode, for web
   installs only), and a table of Feature | Spec | Sub-issue:
   - manifest hashes → `manifest-hashes.md` → #264
   - installer update mode → `installer-update-mode.md` → #265
   - `tingle update` command → `update-command.md` → #266
   - user guide → n/a (rules in section 8) → #267
   - cleanup: remove these specs and the index row → n/a → #270
2. **Merge order:** #269 → #264 → #265 → #266 → #267 → #270, each depending
   on the previous one. #264–#266 must be merged before the **0.4.0** tag.
3. **Scope:** the in/out-of-scope lists from #263. Git-clone updates are
   #268. Also the accepted gap: 0.3.x installs have no `tingle update`.
4. **File formats:** the `MANIFEST` line format (`<64-hex>  <path>`, two
   spaces, `LC_ALL=C`-sorted by path, excluding itself) and the `tingle.json`
   schema (`version`, `repo`, `manifest: [{path, sha256}]`). The old path-only
   `manifest: ["path"]` must still be read. "Tracks hashes" is decided by
   format, not by version.
5. **Env vars and CLI:**
   - installer: `TINGLE_UPDATE_TARGET`, `TINGLE_UPDATE_FORCE`,
     `TINGLE_REPO`, `TINGLE_VERSION`;
   - command: `tingle update [--check] [--force] [<version>]`,
     `TINGLE_VERSION`, `TINGLE_ASSUME_YES`;
   - test-only hooks: `TINGLE_RELEASE_API_URL` (default
     `https://api.github.com/repos/<repo>`) and `TINGLE_RELEASE_BASE_URL`
     (default `https://github.com/<repo>/releases/download`), documented in
     script headers only.
6. **Version rules:** `X.Y.Z` or `X.Y.Z-<suffix>`, no `v`. The 0.4.0 floor
   (E2). `"unknown"` counts as out of date. Downgrades to 0.4.0 or later are
   allowed. "Latest" means the latest stable release.
7. **Guarantees and exit codes:** every abort path "changes nothing". A
   non-zero exit on every refusal (git checkout, unknown install, corrupt
   `tingle.json`, network, checksum, edited files without `--force`, lock
   held). Exit 0 for success, already up to date, and `--check`.
8. **Rules for #267 (user guide):** what `docs/guides/update.md` must
   cover (see the list in #270's first bullet), that the test-only hooks are
   not documented there, the index link, the `install.md` cross-link, and the
   new installer message pointing at `tingle update`.
9. **Edge-case index:** a table of E1–E15 and E9b with one line each, and
   which spec owns each one (#265: E1, E3, E5, E11–E13, E15; #266: E2, E4,
   E6–E10, E9b, E14). E3 is checked by both.

## Files to Change
- `docs/agents/specs/update_command/README.md`: new.
