# `tingle uninstall`

Remove tingle's PATH and bash completion wiring from `~/.bashrc`.

## What it does

`tingle uninstall` undoes what [`tingle install`](install.md) set up. It
removes the tingle marker block from `~/.bashrc`, so new shells no longer
have tingle's `bin/` folder on `PATH` or load tingle's bash completion.

It does not delete tingle itself: the tingle folder is left in place.

## Usage

```
tingle uninstall
```

The command takes no options.

## What it changes

tingle looks in `~/.bashrc` for its block, including the start and end
markers:

```
# >>> tingle >>>
export PATH="/path/to/tingle/bin:$PATH"
source "/path/to/tingle/completions/tingle.bash"
# <<< tingle <<<
```

That block is removed. Nothing else in `~/.bashrc` is touched.

When it finishes, it prints:

```
tingle uninstalled from /home/you/.bashrc. Restart your shell to drop it from PATH. The tingle folder (/path/to/tingle) was left in place; delete it manually if you no longer need it.
```

Shells that are already open keep tingle on their `PATH` until you close
them.

## Running it again

Running `tingle uninstall` more than once is safe. If `~/.bashrc` does not
exist, or does not contain the tingle block, nothing is changed and tingle
prints:

```
tingle is not installed in /home/you/.bashrc
```

## Removing the tingle folder

`tingle uninstall` never deletes files outside `~/.bashrc`. If you no longer
need tingle, delete its folder yourself:

- **Web installer:** tingle lives in `~/.tingle`:

  ```
  rm -rf ~/.tingle
  ```

- **Cloned repository:** delete your clone.

## Check that it worked

1. Open a new terminal.
2. Run:

   ```
   command -v tingle
   ```

   It should print nothing, meaning `tingle` is no longer on your `PATH`.
