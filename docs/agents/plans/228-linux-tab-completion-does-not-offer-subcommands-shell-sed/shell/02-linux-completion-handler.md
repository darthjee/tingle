# Add shell/linux/completion.sh
Create an executable `shell/linux/completion.sh`, following the header-comment style of `shell/linux/executor.sh`. It receives the raw argv (the subcommand onward, with the in-progress word last and possibly empty). Drop the last element and look only at the committed words. Don't use `getopts` or any other strict parsing.

- No committed words: print `shell sed`.
- First committed word `sed`: print `__tingle_files__`.
- Otherwise (`shell` or unknown): print nothing.

Keep the subcommand list in one variable (for example `SUBCOMMANDS="shell sed"`) with a comment saying it must match the `case` in `executor.sh`. The script must be safe under `set -euo pipefail` with zero arguments or an empty last argument. It always exits 0, and it must not source `docker_run.sh` or call Docker.

## Files to Change
- `shell/linux/completion.sh` — new completion handler (mode 755).
