# Cli Plan: check_file_size: add --min-level display filter

Main plan: [plan.md](plan.md)

## Shared contracts

- Document `--min-level ok|warn|error|critical` (default `ok`): it shows only files at that level or higher, before `--top`. Display only: the summary, `Total:` and `--fail-on` count every analysed file.
- `--top` no longer cuts the summary.

## Implementation Steps

### Step 1 — Update `long_help`
In `commands/python.json` → `check_file_size.long_help`, add a `Display:` section before `CI gate:`, with the same alignment as the other options:

```
Display:
    --top N                        Show only the N largest files (0 = all).
    --min-level ok|warn|error|critical
                                   Show only files at this level or higher
                                   (default: ok). Applied before --top.
                                   Summary, Total and --fail-on always count
                                   every analysed file.
```

Change the `--fail-on` text from "(counted before --top)" to "(counts every analysed file, including rows hidden by --top or --min-level)". Add the examples `./check_file_size.py ./src --min-level warn` and `./check_file_size.py ./src --min-level error --top 5`.

## Files to Change
- `commands/python.json` — `check_file_size.long_help`.

## Notes
- Keep the JSON valid (escaped `\n`). Check it with `python -m json.tool commands/python.json`.
