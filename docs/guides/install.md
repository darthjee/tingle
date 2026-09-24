# `tingle install`

Install tingle onto `PATH` and enable bash completion.

## What it does

`tingle install` wires tingle into your bash shell. It appends a small marker
block to `~/.bashrc` that adds tingle's `bin/` folder to your `PATH` and loads
tingle's bash completion script, so you can run `tingle` from anywhere and use
`tingle <TAB>` to complete command names.

## Prerequisites

- `bash`.
- `jq`, which `bin/tingle` needs to run (and which the completion script
  uses too).

## Supported shells

tingle only wires itself into **bash**, through `~/.bashrc`. Other shells are
not configured:

- **zsh** (the default shell on macOS) and **fish** are not supported. If you
  use one of them, add tingle's `bin/` folder to your `PATH` yourself in that
  shell's configuration file.
- **macOS and bash:** Terminal starts bash as a login shell, which reads
  `~/.bash_profile` instead of `~/.bashrc`. For the tingle block to take
  effect, make sure `~/.bash_profile` loads `~/.bashrc` by adding this line to
  it:

  ```
  [ -f ~/.bashrc ] && source ~/.bashrc
  ```

## When to run it

- **Web installer:** if you installed tingle with the one-line installer
  described in the [Installation](../../README.md#installation) section of
  the main README, you do not need to run this yourself. The installer
  unpacks tingle to `~/.tingle` and runs `tingle install` as its last step.
- **Cloned repository:** if you cloned the repo manually, `tingle` is not on
  your `PATH` yet. Run it from the repository root the first time:

  ```
  ./bin/tingle install
  ```

## Usage

```
tingle install
```

The command takes no options.

## What it changes

If `~/.bashrc` does not exist, it is created. Then tingle appends a blank line
followed by this block, where `/path/to/tingle` is the folder tingle lives in
(for example `~/.tingle` or wherever you cloned it):

```
# >>> tingle >>>
export PATH="/path/to/tingle/bin:$PATH"
source "/path/to/tingle/completions/tingle.bash"
# <<< tingle <<<
```

Nothing else in `~/.bashrc` is touched: tingle only ever writes or rewrites
its own block, between the `# >>> tingle >>>` and `# <<< tingle <<<` markers.
The rest of the file is never rewritten or removed.

When it finishes, it prints:

```
tingle installed. Run 'source /home/you/.bashrc' or restart your shell to start using it.
```

## Running it again

Running `tingle install` more than once is safe. What happens depends on
where the existing block points:

- **Same folder:** if `~/.bashrc` already contains the tingle block and it
  points to the folder you are running tingle from, the file is left
  unchanged and tingle prints:

  ```
  tingle is already installed in /home/you/.bashrc
  ```

- **Moved or reinstalled elsewhere:** if the block points to a different
  folder (for example, you moved your clone or reinstalled tingle in a new
  location), tingle rewrites the block in place so it points to the new
  folder, and prints:

  ```
  tingle install updated in /home/you/.bashrc (now pointing to /new/path/to/tingle). Run 'source /home/you/.bashrc' or restart your shell to pick it up.
  ```

In both cases, the rest of `~/.bashrc` is never touched.

## Check that it worked

1. Reload your shell configuration, or open a new terminal:

   ```
   source ~/.bashrc
   ```

2. Run `tingle` with no arguments. You should see the list of available
   commands.
3. Type `tingle ` followed by <kbd>TAB</kbd>. Bash should suggest the
   available command names.

## Uninstalling

To remove the tingle block from `~/.bashrc`, run `tingle uninstall`. See the
[`uninstall` guide](uninstall.md) for details.
