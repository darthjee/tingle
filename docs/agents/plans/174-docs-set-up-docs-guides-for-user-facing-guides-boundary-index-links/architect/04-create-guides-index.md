# Create the guides index

Create `docs/guides/README.md`:

- A title (e.g. `# Tingle User Guides`) and a short intro saying these are
  end-user guides, one per `tingle` command, and that `tingle --help
  <command>` gives a quick summary.
- A list of guides with a placeholder for each command: `install`,
  `linux`, `kube`, `check_file_size`. Each placeholder shows the command
  name, its one-line description (reuse the `short_help` wording from
  `commands/*.json`), and a "guide coming soon" marker. **Do not add links**
  to `docs/guides/<command>.md` yet, because those files don't exist. Each
  of #175–#178 replaces its own placeholder with a link.
- Keep one entry per line so the sibling sub-issues each edit a separate
  line and don't conflict.

## Files to Change
- `docs/guides/README.md` — new index with placeholder entries.
