# `tingle linux`

Run GNU/Linux tools (sed, shell) inside a container.

## What it does

Some command-line tools on your machine behave differently from their
GNU/Linux versions. For example, macOS ships BSD `sed`, where `-i` needs a
backup-suffix argument (`sed -i '' 's/a/b/' file`), while GNU `sed` takes
`-i` on its own. Differences like this break scripts and muscle memory.

`tingle linux` runs the real GNU/Linux tool inside a Docker container,
against the files in your current directory, so you get the same behaviour
you would get on Linux.

## Prerequisites

- Docker installed, with the Docker daemon running.
- The container image `darthjee/tingle:<version>` is pulled automatically
  the first time you use the command, so the first run may take longer.

## Usage

```
tingle linux shell
tingle linux sed <sed-args...>
```

If you enabled bash completion with `tingle install`, pressing Tab completes
the `shell` and `sed` subcommands, and file and folder names for `sed`
arguments.

## `tingle linux shell`

```
tingle linux shell
```

Opens an interactive `bash` shell (with a terminal attached) inside the
container, in your current directory. From there you can run Linux-native
tools directly against your files. Type `exit` to leave the shell and
return to your host.

## `tingle linux sed`

```
tingle linux sed <sed-args...>
```

Runs GNU `sed` inside the container. All arguments are passed to `sed`
unchanged. Standard input is attached (without a terminal), so you can use
it both on files and in pipelines.

Edit a file in place, using GNU `-i` syntax (no backup-suffix argument,
unlike BSD `sed`):

```
tingle linux sed -i 's/foo/bar/' somefile.txt
```

Pipe standard input through GNU `sed`; the result is written to standard
output:

```
cat file | tingle linux sed 's/a/b/'
```

## How your files are mounted

- Your current directory is mounted into the container at the same path
  and used as the working directory, so relative paths behave exactly as
  they do on your host.
- Only the current directory (and everything below it) is visible inside
  the container. A path such as `../other.txt`, or an absolute path outside
  the current directory, will not be found. If you need files from several
  places, `cd` to a common parent directory first.
- The container runs as your host user and group IDs, so files it creates
  or edits stay owned by you.
- Each run uses a fresh container that is removed when the command ends.
  Only changes made inside the mounted directory are kept.

## Errors

- Running `tingle linux` without a subcommand, or with an unknown one,
  prints this to standard error and exits with status 1:

  ```
  tingle linux: unknown subcommand '<name>'
  ```

  When no subcommand is given, `<name>` is empty (`''`).

- If Docker is not installed or the daemon is not running, the error
  message comes from `docker` itself.

## Quick help

For a short summary of the command, run:

```
tingle --help linux
```
