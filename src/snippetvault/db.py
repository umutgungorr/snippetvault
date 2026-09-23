"""Database management and SQLite repository for SnippetVault."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Sequence

from snippetvault.models import Snippet

DEFAULT_DB_DIR = Path.home() / ".snippetvault"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "vault.db"


def get_default_db_path() -> Path:
    env_path = os.environ.get("SNIPPETVAULT_DB_PATH")
    if env_path:
        return Path(env_path)
    DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_DB_PATH


class Database:
    """Manages SQLite storage for snippets."""

    def __init__(self, db_path: Path | str | None = None):
        self.path = Path(db_path) if db_path else get_default_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    command TEXT NOT NULL,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    description TEXT NOT NULL DEFAULT '',
                    language TEXT NOT NULL DEFAULT 'bash',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    times_used INTEGER NOT NULL DEFAULT 0,
                    last_used_at TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_snippets_title ON snippets(title);
                CREATE INDEX IF NOT EXISTS idx_snippets_language ON snippets(language);
            """)

    def insert(self, snippet: Snippet) -> Snippet:
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO snippets (
                    title, command, tags_json, description, language,
                    created_at, updated_at, times_used, last_used_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snippet.title,
                    snippet.command,
                    json.dumps(snippet.tags),
                    snippet.description,
                    snippet.language,
                    snippet.created_at,
                    snippet.updated_at,
                    snippet.times_used,
                    snippet.last_used_at,
                ),
            )
            snippet.id = cur.lastrowid
            return snippet

    def update(self, snippet: Snippet) -> bool:
        if snippet.id is None:
            return False
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                UPDATE snippets SET
                    title = ?,
                    command = ?,
                    tags_json = ?,
                    description = ?,
                    language = ?,
                    updated_at = ?,
                    times_used = ?,
                    last_used_at = ?
                WHERE id = ?
                """,
                (
                    snippet.title,
                    snippet.command,
                    json.dumps(snippet.tags),
                    snippet.description,
                    snippet.language,
                    snippet.updated_at,
                    snippet.times_used,
                    snippet.last_used_at,
                    snippet.id,
                ),
            )
            return cur.rowcount > 0

    def delete(self, snippet_id: int) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
            return cur.rowcount > 0

    def get_by_id(self, snippet_id: int) -> Snippet | None:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,)).fetchone()
            if not row:
                return None
            return self._row_to_snippet(row)

    def get_all(self) -> list[Snippet]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM snippets ORDER BY id DESC").fetchall()
            return [self._row_to_snippet(r) for r in rows]

    def increment_usage(self, snippet_id: int) -> None:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE snippets SET times_used = times_used + 1, last_used_at = ? WHERE id = ?",
                (now, snippet_id),
            )

    def _row_to_snippet(self, row: sqlite3.Row) -> Snippet:
        tags = []
        with_tags = row["tags_json"]
        if with_tags:
            try:
                tags = json.loads(with_tags)
            except Exception:
                tags = []
        return Snippet(
            id=row["id"],
            title=row["title"],
            command=row["command"],
            tags=tags,
            description=row["description"],
            language=row["language"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            times_used=row["times_used"],
            last_used_at=row["last_used_at"],
        )
