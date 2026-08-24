# Create the commands/ mapping directory

Create the root-level `commands/` directory with one shell-sourceable file per language, `key=value` mappings of command name → script path (relative to `TINGLE_FOLDER`):

**`commands/python.sh`**
```bash
# commands/python.sh
# Maps command names to script paths (relative to TINGLE_FOLDER)
check_file_size="python/check_file_size.py"
```

**`commands/node.sh`** (empty scaffold — no node commands exist yet)
```bash
# commands/node.sh
# Maps command names to script paths (relative to TINGLE_FOLDER)
# (add node commands here)
```

**`commands/shell.sh`** (empty scaffold — no shell commands exist yet)
```bash
# commands/shell.sh
# Maps command names to script paths (relative to TINGLE_FOLDER)
# (add shell commands here)
```

Duplicate command names across these files are not guarded against — last-sourced (glob/alphabetical order) silently wins, per the issue's Edge Cases decision.

## Files to Change

- `commands/python.sh` — new file, `check_file_size` mapping.
- `commands/node.sh` — new file, empty scaffold.
- `commands/shell.sh` — new file, empty scaffold.
