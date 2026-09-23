"""Data models for SnippetVault."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Snippet:
    """Represents a stored command or code snippet."""

    id: int | None
    title: str
    command: str
    tags: list[str]
    description: str = ""
    language: str = "bash"
    created_at: str = ""
    updated_at: str = ""
    times_used: int = 0
    last_used_at: str | None = None

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Snippet:
        tags = data.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            command=data.get("command", ""),
            tags=tags,
            description=data.get("description", ""),
            language=data.get("language", "bash"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            times_used=int(data.get("times_used", 0)),
            last_used_at=data.get("last_used_at"),
        )


@dataclass(slots=True)
class SearchMatch:
    """Represents a snippet search result with relevance score."""

    snippet: Snippet
    score: float
    matched_by: str  # 'title', 'tag', 'command', 'description'
