# SnippetVault 🗄️⚡

[![PyPI version](https://img.shields.io/pypi/v/snippetvault.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/snippetvault/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero%20external-success.svg)]()
[![Tests](https://img.shields.io/badge/tests-passed-brightgreen.svg)]()

> **SnippetVault is an ultra-fast, zero-dependency terminal command & code snippet organizer with fuzzy search, tag indexing, OS clipboard copying, and safe execution.**  
> Stop losing complex `docker compose`, `kubectl`, `ffmpeg`, regex, or git commands in messy text files or bash history.

---

## 🚀 Quick Start

### Installation

```bash
pip install snippetvault
```

### 1. Save a Command
```bash
snippetvault add "docker compose -f docker-compose.prod.yml up -d --build" \
  -t "Prod Docker Deploy" \
  --tags docker,prod,compose \
  -d "Spins up production containers with zero downtime rebuild"
```

### 2. Search & Fuzzy Find
```bash
snippetvault find docker
```
Output:
```text
Search Results for 'docker' (2 matches)
----------------------------------------------------------------------
#1   Prod Docker Deploy [docker, prod, compose] (score: 1.00)
     $ docker compose -f docker-compose.prod.yml up -d --build
#2   Docker Prune Unused Images [docker, cleanup] (score: 0.95)
     $ docker image prune -a --filter "until=72h"
----------------------------------------------------------------------
```

### 3. Copy to Clipboard
```bash
snippetvault copy 1
# ✓ Snippet #1 copied to clipboard! Ready to paste (Ctrl+V / Cmd+V).
```

### 4. Safe Run in Terminal
```bash
snippetvault run 1
# Ready to execute snippet #1:
# $ docker compose -f docker-compose.prod.yml up -d --build
# Execute this command? [y/N]: y
```

---

## 🌟 Features & Architecture

- **Zero External Dependencies**: Powered strictly by Python's Standard Library (`sqlite3`, `argparse`, `difflib`, `shlex`, `json`, `pathlib`). Instant execution with zero latency.
- **Embedded SQLite WAL Engine**: Data is safely stored locally at `~/.snippetvault/vault.db` with Write-Ahead Logging for high concurrency and zero corruption.
- **Fuzzy Search & Ranking**: Combines exact tag matches, substring queries, and Levenshtein sequence matching to find what you need even with typos.
- **Cross-Platform Clipboard**: Works seamlessly on macOS (`pbcopy`), Linux (`wl-copy`, `xclip`, `xsel`), and Windows (`clip.exe`).
- **Backup & Portability**: 1-click JSON export and import (`snippetvault export -o backup.json`).

---

## 📖 CLI Commands Reference

| Command | Arguments | Description |
|---------|-----------|-------------|
| `add` | `<cmd> -t <title> [--tags ...] [-d ...]` | Save a new snippet to your vault |
| `list` | `[--tag <tag>] [--json]` | List all stored snippets |
| `find` | `<query> [--limit 10] [--json]` | Fuzzy search snippets across titles and tags |
| `get` | `<id>` | Display complete snippet details |
| `copy` | `<id>` | Copy snippet command to OS clipboard |
| `run` | `<id> [-y/--yes]` | Execute snippet with optional confirmation |
| `delete`| `<id>` | Remove snippet from vault |
| `export`| `[-o <file.json>]` | Export vault database to JSON |
| `import`| `<file.json> [--overwrite]` | Import snippets from JSON backup |
| `stats` | — | Display usage counts, top tags, and stats |

---

## 🧪 Running Tests

```bash
uv run pytest
```

---

## 📄 License

MIT © [Umut Güngör](https://github.com/umutgungorr)
