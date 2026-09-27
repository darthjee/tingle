# Complete --isolated after shell
In `shell/linux/completion.sh`, add a `shell)` case to the `case "${committed[0]}"` that prints `--isolated`, unless `--isolated` is already among the committed words. Update the header comment: it currently says nothing is printed after `shell`. The script must still never start Docker and must always exit 0.

## Files to Change
- `shell/linux/completion.sh` — offer `--isolated` after `shell`, and update the header comment.
