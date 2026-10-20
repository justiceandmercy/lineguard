# lineguard

Enforce a maximum line length and forbid trailing whitespace across a codebase.
`lineguard` is a small, dependency-free CLI that scans source files and reports
lines that exceed a configurable limit or contain trailing spaces/tabs. It can
also fix trailing whitespace in place, making it handy for CI and pre-commit hooks.

## Features

- Reports lines longer than a configurable limit (default 88).
- Detects trailing whitespace (spaces/tabs) on any line.
- Optional in-place fixing of trailing whitespace (`--fix`).
- Configurable extension filter and maximum line length.
- Human-readable or `--json` output.
- Non-zero exit code when issues are found (CI-friendly).
- No external dependencies, no network access.

## Install

```bash
pip install -e .
```

Or run directly:

```bash
python -m lineguard.cli .
```

## Usage

Scan the current directory:

```bash
lineguard .
```

Scan with a custom line limit:

```bash
lineguard src/ --max-len 100
```

Only check line length (ignore trailing whitespace):

```bash
lineguard . --no-trailing
```

Restrict to certain extensions:

```bash
lineguard . --ext .py,.md
```

Fix trailing whitespace in place:

```bash
lineguard . --fix
```

Emit JSON:

```bash
lineguard . --json
```

Example output:

```
src/app.py:12: line too long (120 > 88)
src/app.py:18: trailing whitespace

Total: 2
```

## License

MIT