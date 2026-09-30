# Write subcommand.md (#295)
Create `docs/agents/specs/code_check/rubycritic/subcommand.md`, linking #295 at the top. This is the largest spec.

It must specify:
- **Dispatch:** `SUBCOMMANDS["rubycritic"]` in `python/code_check/executor.py`, the new package `python/code_check/rubycritic/`, `long_help` in `commands/python.json`, and completion for the subcommand and its flags.
- **Flags added here:**
  - `--warn/--error/--critical`: floats ≥ 0, defaults 100/200/400
  - `--top`, `--min-level`, `--fail-on`
  - `--image`
  
  Include how levels are computed from complexity, with the same comparisons as `file_size`.
- **Preflight:** `docker` on the PATH, then `docker info`, with the exact error texts.
- **Image resolution:** default `darthjee/tingle_rubycritic:<version>`, with the version read the way `shell/linux/docker_run.sh` reads `shell/linux/VERSION`. Say which file is the source of truth for the tingle version at runtime. `--image` overrides it.
- **Run:** the exact `docker run` argument list: uid/gid, `--network none`, `-v <path>:/src:ro`, `-w /src`, `-i`, with the file list written to stdin.
- **JSON contract:** a trimmed real sample from step 01, the exact JSON paths used for each column and for the summary score, and how paths map back to paths relative to `<path>`.
- **Report layout:** header lines, column order and widths (mirroring `file_size`'s reporter), sorting (complexity, highest first), the summary line, and the `Score:` line. Give a full example.
- **Exit codes:** 0, 1 and 2, with every exit-1 cause.
- **Edge cases**, each with its exact behaviour and message:
  - `PARSE` rows, with the detection rule from step 01. They count as skipped and never trigger `--fail-on`.
  - A single-file `<path>`: mount its parent directory.
  - No `.rb` files: an empty report, exit 0, no container started.
  - A mount failure, with the Docker Desktop file-sharing hint.
  - Filenames containing a newline: skipped with a warning.
  - Files RubyCritic drops: reported as `OK` with complexity 0.
  - `<path>` missing or unreadable.
- **Error and warning texts:** every one, verbatim, in `file_size`'s `Error:`/`Warning:` style.
- **File selection in this sub-issue:** only `.rb` files minus the default excludes. The rest comes in #296.
- **Test expectations:** Docker/subprocess is mocked, with the cases to cover.

## Files to Change
- `docs/agents/specs/code_check/rubycritic/subcommand.md`: new.
