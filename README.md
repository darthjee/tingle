# Tingle

Personal repository of everyday utility scripts — a code "Swiss Army knife".

Scripts in **shell**, **Python** and **Node.js** for simple, recurring tasks:
file scraping, bulk renaming, copying files between git branches,
and whatever else comes up in daily work.

## Name Origin

The name **Tingle** is a tribute to the eccentric and iconic character from the
*The Legend of Zelda* series (reference: [Zelda Wiki](https://zelda.fandom.com/wiki/Tingle)).

In the game universe, Tingle is a "fairy" cartographer who lives to provide maps, items
and utilities to the hero — always in a peculiar, fun and unusual way. He exists
to offer the right tool at the right time.

By analogy, **Tingle** is the repository where I keep the small utilities
I use in my daily work: each script is a small but essential tool,
ready to solve the task of the moment — with no single theme, but each one doing
its part. Like Tingle, the project is light, versatile and a bit peculiar.

## Structure

```
tingle/
├── bin/            # Callable entry points (on PATH), calling into shell/python/node
├── shell/          # Bash/Shell scripts
├── python/         # Python scripts
├── node/           # Node.js scripts
└── README.md
```

## Scripts

| Script | Language | Description |
| --- | --- | --- |
| `check_file_size` | Python | Token efficiency triage: lists source files by line count against configurable warn/error/critical thresholds. |

## Usage

Each script is independent and can be run directly. Check each script's header
for usage instructions and dependencies.

## License

[MIT 2026](LICENSE)
