# Spec: the `tingle_rubycritic` Docker image

Sub-issue: #293. Parent: #290. Shared contracts: [README.md](README.md).

The image runs RubyCritic for `tingle code_check rubycritic`. Tingle sends a
list of files on stdin and reads one JSON object on stdout. This spec covers
the image source and its local build. Publishing is in
[release.md](release.md).

## 1. Location and files

The image lives in a new top-level folder, `docker/rubycritic/`, owned by the
`shell` agent (see [README.md](README.md#ownership-of-docker)). #293 also adds
the folder to `.claude/agents/shell.md` and
`docs/agents/folder-structure.md`.

| Path | Content |
|------|---------|
| `docker/rubycritic/Dockerfile` | The image (section 2). |
| `docker/rubycritic/Gemfile` | `source "https://rubygems.org"` and `gem "rubycritic", "5.0.0"`, nothing else. |
| `docker/rubycritic/Gemfile.lock` | The resolved lock (section 3), committed. |
| `docker/rubycritic/entrypoint.rb` | The entrypoint wrapper (section 4). |
| `docker/rubycritic/fixture/` | The smoke-test fixture (section 6). |
| `docker/rubycritic/.dockerignore` | Excludes `fixture/` (and, from #294, the Docker Hub description files) from the build context. |

The build context is `docker/rubycritic/` itself, not the repo root:

```
docker buildx build -t <tag> docker/rubycritic
```

So every `COPY` source is relative to `docker/rubycritic/`.

## 2. Dockerfile

- **Base image:** `ruby:3.3.12-slim` (Debian trixie), pinned by its
  multi-platform index digest in a top-level `ARG BASE_IMAGE`, the same way
  `shell/linux/Dockerfile` pins its base:

  ```
  ARG BASE_IMAGE=ruby:3.3.12-slim@sha256:379ffc9ca20cae2655cb80cac53ee23e1e7d859c03a4cceb7f567d6ce4873cee
  ```

  The digest resolves on `linux/amd64` and `linux/arm64`. Bumping the Ruby
  patch or the digest is a deliberate change (see section 8).
- **Two stages.**
  - A `build` stage installs `build-essential` (`--no-install-recommends`,
    version pinned as hadolint DL3008 requires; `12.12` at the time of
    writing) and runs `bundle install` from `Gemfile` + `Gemfile.lock`. The
    build tools are needed: `prism 1.9.0` compiles a native extension, and
    `gem install rubycritic` fails with `extconf failed` on the plain slim
    image.
  - The final stage starts again from `BASE_IMAGE`, copies the installed
    gems (`/usr/local/bundle`) and the Gemfile pair from the `build` stage,
    and installs no apt package. It has no compiler.
- **Bundler settings** (as `ENV` in both stages):
  `BUNDLE_GEMFILE=/opt/tingle_rubycritic/Gemfile` and `BUNDLE_FROZEN=true`,
  so `bundle install` fails if the lock does not match the Gemfile, and the
  runtime loads exactly the locked versions.
- **No git.** Neither stage installs git, and the base image has none
  (`command -v git` fails). Without git, RubyCritic skips version control: it
  computes no churn, and git's "dubious ownership" error can't happen under a
  foreign uid. RubyCritic then prints
  `RubyCritic can provide more feedback if you use a Git, Mercurial or Perforce repository. Churn will not be calculated.`
  This notice is expected and goes to stderr (section 4).
- **Locale:** the base image's `LANG=C.UTF-8` must stay, so source files are
  read as UTF-8.
- **User:** the image ends with `USER 1000:1000`. Tingle always overrides it
  with `--user <uid>:<gid>`.
- **Entrypoint:** `ENTRYPOINT ["ruby", "/opt/tingle_rubycritic/entrypoint.rb"]`
  and no `CMD`. The entrypoint takes no arguments.

## 3. Pinned versions

| Component | Version | Pinned by |
|-----------|---------|-----------|
| Ruby | `3.3.12` (`ruby:3.3.12-slim`, digest above) | `ARG BASE_IMAGE` |
| Bundler | `2.5.22` (shipped with the base image) | `BUNDLED WITH` in `Gemfile.lock` |
| `rubycritic` | `5.0.0` (latest stable, 2026-01-27) | `Gemfile` (`= 5.0.0`) and `Gemfile.lock` |
| `flog` | `4.9.4` | `Gemfile.lock` |
| `flay` | `2.14.4` | `Gemfile.lock` |
| `reek` | `6.5.0` | `Gemfile.lock` |
| `parser` | `3.3.12.0` | `Gemfile.lock` |
| `prism` | `1.9.0` | `Gemfile.lock` |
| `ruby_parser` | `3.22.0` | `Gemfile.lock` |

- `Gemfile.lock` lists the platforms `aarch64-linux` and `x86_64-linux`, and
  not `ruby`, so the same lock installs on both architectures. It is
  generated inside the base image with
  `bundle lock --add-platform x86_64-linux aarch64-linux` and
  `bundle lock --remove-platform ruby`.
- `rubycritic 5.0.0` needs Ruby `>= 3.2.0`.

## 4. Entrypoint contract

The entrypoint is a Ruby script that loads the locked bundle
(`require "bundler/setup"`). It is the only process tingle talks to.

### Input

- It reads all of stdin as UTF-8 and splits it on `\n`.
- Each non-blank line is one file path, relative to the working directory
  (`/src`). Blank lines are ignored. Duplicate lines are kept once, at their
  first position.
- It receives no arguments.

### Pre-parse

RubyCritic 5.0.0 aborts the whole run on the first file with a syntax error
(Reek raises `Reek::Errors::SyntaxError`, RubyCritic exits 1 and writes no
report). So, before running RubyCritic, the entrypoint parses every path with
the parser Reek uses, configured as Reek configures it:

```ruby
Reek::Source::SourceCode.new(source: File.read(path), origin: path).syntax_tree
```

- If this raises anything (`StandardError` or `ScriptError`, which covers
  syntax errors, invalid UTF-8 and unreadable or missing files), the path goes
  to `parse_errors` and is **not** passed to RubyCritic.
- Each `parse_errors` entry is `{"path": <the line as received>, "message":
  <the first line of the exception message, stripped>}`, in input order.
  Observed messages: `unexpected token tSTRING` (syntax error) and
  `invalid byte sequence in UTF-8` (bad encoding).

### Run

- When at least one path survives the pre-parse, the entrypoint runs, in
  `/src`:

  ```
  rubycritic --format json --no-browser -p /tmp/out <paths>
  ```

  with the surviving paths as separate arguments, in input order. It runs it
  under the locked bundle (for example `bundle exec rubycritic ...`).
- RubyCritic's stdout **and** stderr are written to the entrypoint's
  stderr. RubyCritic prints its progress lines, the git notice and
  `Score: NN.NN` on stdout, so they must not reach the entrypoint's stdout.
- RubyCritic must never be run with zero paths: with no paths it analyses
  `.`.
- `-p /tmp/out` works with a read-only `/src` and a foreign uid: `/tmp` is
  writable by everyone, and the run needs no extra environment (it was
  checked with `--user 501:20` and the inherited `HOME=/`).

### Output

- On success, stdout holds exactly one JSON object followed by `\n`: the
  object parsed from `/tmp/out/report.json`, with one extra top-level key,
  `parse_errors`. Nothing else is written to stdout.
- When no path survives (all paths failed the pre-parse, or stdin had no
  paths), RubyCritic is not run, and the entrypoint prints:

  ```json
  {"metadata":null,"analysed_modules":[],"score":null,"parse_errors":[...]}
  ```

  with exit status 0. Tingle never starts the container with an empty list,
  but the image must handle it.
- The field paths and meanings are pinned in
  [subcommand.md](subcommand.md#5-rubycritic-json-contract).

### Exit status

| Status | When |
|--------|------|
| `0` | The JSON was printed, including when some or all files are in `parse_errors`. |
| RubyCritic's status (non-zero) | RubyCritic exited non-zero. Nothing is printed on stdout. |
| `1` | `/tmp/out/report.json` is missing or is not valid JSON after a successful RubyCritic run, or any other entrypoint failure. A one-line reason goes to stderr. Nothing is printed on stdout. |

## 5. Runtime environment

Tingle runs the image with the canonical line from
[README.md](README.md#8-image-contract-summary):

```
docker run --rm -i --pull never --network none --security-opt no-new-privileges \
  --user <uid>:<gid> -v <root>:/src:ro -w /src <image>
```

The image must work under that line for any `<uid>:<gid>`, with no network
and with `/src` read-only. It writes only under `/tmp`.

## 6. Smoke-test fixture

`docker/rubycritic/fixture/` holds the step-01 grounding set:

| File | Content | Expected in the output |
|------|---------|------------------------|
| `simple.rb` | A class with one trivial method. | In `analysed_modules`, `complexity` below 5, `rating` `"A"`. |
| `complex.rb` | One method with nested conditionals, loops and a `case` (Flog ~72). | In `analysed_modules`, `complexity` above 50. |
| `dup_a.rb`, `dup_b.rb` | Two classes with the same method body. | Both in `analysed_modules` with `duplication` above 0. |
| `broken.rb` | A method with an unclosed parameter list. | Only in `parse_errors`. |
| `empty.rb` | An empty file. | In `analysed_modules`, `complexity` `0.0`, `methods_count` `0`. |
| `constants_only.rb` | A module with two constants and no method. | In `analysed_modules`, `complexity` `0.0`, `methods_count` `0`. |

The smoke test pipes the list of these files (one per line) into the
canonical run line with `-v <fixture>:/src:ro` and `--user 501:20`, and
asserts that:

- the exit status is 0;
- stdout parses as one JSON object;
- `metadata.rubycritic.version` is `"5.0.0"`;
- the set of `analysed_modules[].path` is exactly the six non-broken files;
- `parse_errors[].path` is exactly `["broken.rb"]`;
- `score` is a number between 0 and 100;
- the per-file expectations in the table hold.

It also asserts that `command -v git` fails inside the image (with
`--entrypoint sh`), and that empty stdin prints the empty object from
section 4 with exit 0. The release pipeline runs it per platform (see
[release.md](release.md#4-pipeline)).

## 7. Local build

The root `Makefile` gets a `rubycritic-image` target with a single recipe
line (tab-indented, as Make requires) that runs:

```sh
docker build -t tingle_rubycritic:dev docker/rubycritic
```

`make rubycritic-image` builds `tingle_rubycritic:dev` for the host
architecture. It is used with
`tingle code_check rubycritic <path> --image tingle_rubycritic:dev` for
end-to-end tests before the image is published.

Verification for #293:

- `docker buildx build --platform linux/amd64 docker/rubycritic` and the same
  for `linux/arm64` succeed.
- The smoke test in section 6 passes against `tingle_rubycritic:dev`.

## 8. Bumping versions

Nothing bumps the pins automatically. Bumping Ruby (tag and digest) or
RubyCritic is a deliberate change:

1. Update `ARG BASE_IMAGE` (tag and index digest, for example from
   `docker buildx imagetools inspect ruby:3.3.N-slim`).
2. For RubyCritic, update the version in `Gemfile`, then regenerate
   `Gemfile.lock` inside the new base image with the commands in section 3.
3. Re-run the smoke test on both platforms. If the JSON shape changed,
   update [subcommand.md](subcommand.md#5-rubycritic-json-contract) (or, once
   the specs are removed, `docs/agents/tingle-rubycritic-image.md`) and the
   Python parser in the same change.
