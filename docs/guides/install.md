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

Nothing else in `~/.bashrc` is touched: existing content is never rewritten
or removed.

When it finishes, it prints:

```
tingle installed. Run 'source /home/you/.bashrc' or restart your shell to start using it.
```

## Running it again

Running `tingle install` more than once is safe. If `~/.bashrc` already
contains the `# >>> tingle >>>` marker, tingle leaves the file unchanged and
prints:

```
tingle is already installed in /home/you/.bashrc
```

## Check that it worked

1. Reload your shell configuration, or open a new terminal:

   ```
   source ~/.bashrc
   ```

2. Run `tingle` with no arguments. You should see the list of available
   commands.
3. Type `tingle ` followed by <kbd>TAB</kbd>. Bash should suggest the
   available command names.
