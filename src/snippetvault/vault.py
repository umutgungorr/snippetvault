"""Core service logic for SnippetVault."""

from __future__ import annotations

import difflib
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from snippetvault.clipboard import copy_to_clipboard
from snippetvault.db import Database
from snippetvault.models import SearchMatch, Snippet


class VaultService:
    """Business operations on snippets."""

    def __init__(self, db: Database | None = None):
        self.db = db or Database()

    def add_snippet(
        self,
        title: str,
        command: str,
        tags: list[str] | None = None,
        description: str = "",
        language: str = "bash",
    ) -> Snippet:
        title = title.strip()
        command = command.strip()
        if not title:
            raise ValueError("Snippet title cannot be empty.")
        if not command:
            raise ValueError("Snippet command cannot be empty.")

        clean_tags = [t.strip().lower() for t in (tags or []) if t.strip()]
        snippet = Snippet(
            id=None,
            title=title,
            command=command,
            tags=sorted(set(clean_tags)),
            description=description.strip(),
            language=language.strip().lower() or "bash",
        )
        return self.db.insert(snippet)

    def list_snippets(self, tag: str | None = None) -> list[Snippet]:
        all_snippets = self.db.get_all()
        if not tag:
            return all_snippets
        target_tag = tag.strip().lower()
        return [s for s in all_snippets if target_tag in [t.lower() for t in s.tags]]

    def search(self, query: str, limit: int = 15) -> list[SearchMatch]:
        query = query.strip().lower()
        if not query:
            return [SearchMatch(s, 1.0, "all") for s in self.db.get_all()[:limit]]

        all_snippets = self.db.get_all()
        matches: list[SearchMatch] = []

        for s in all_snippets:
            title_lower = s.title.lower()
            cmd_lower = s.command.lower()
            desc_lower = s.description.lower()
            tags_lower = [t.lower() for t in s.tags]

            score = 0.0
            matched_by = "none"

            # Exact or prefix tag match
            if query in tags_lower:
                score = max(score, 1.0)
                matched_by = "tag"
            elif any(t.startswith(query) for t in tags_lower):
                score = max(score, 0.9)
                matched_by = "tag"

            # Substring or fuzzy title match
            if query in title_lower:
                score = max(score, 0.95)
                matched_by = "title"
            else:
                ratio = difflib.SequenceMatcher(None, query, title_lower).ratio()
                title_words = title_lower.split()
                best_word_ratio = max(
                    (difflib.SequenceMatcher(None, query, w).ratio() for w in title_words),
                    default=0.0
                )
                effective_ratio = max(ratio, best_word_ratio)
                if effective_ratio > 0.6:
                    score = max(score, effective_ratio * 0.9)
                    matched_by = "title"

            # Command substring
            if query in cmd_lower:
                score = max(score, 0.85)
                if matched_by == "none":
                    matched_by = "command"

            # Description substring
            if desc_lower and query in desc_lower:
                score = max(score, 0.7)
                if matched_by == "none":
                    matched_by = "description"

            if score >= 0.5:
                matches.append(SearchMatch(s, score, matched_by))

        matches.sort(key=lambda m: (m.score, m.snippet.times_used), reverse=True)
        return matches[:limit]

    def get_by_id(self, snippet_id: int) -> Snippet | None:
        return self.db.get_by_id(snippet_id)

    def delete_snippet(self, snippet_id: int) -> bool:
        return self.db.delete(snippet_id)

    def copy_snippet(self, snippet_id: int) -> tuple[bool, Snippet | None]:
        snippet = self.db.get_by_id(snippet_id)
        if not snippet:
            return False, None
        ok = copy_to_clipboard(snippet.command)
        self.db.increment_usage(snippet_id)
        return ok, snippet

    def run_snippet(self, snippet_id: int) -> tuple[int, str, str]:
        snippet = self.db.get_by_id(snippet_id)
        if not snippet:
            raise ValueError(f"Snippet #{snippet_id} not found.")

        self.db.increment_usage(snippet_id)
        # Execute using default shell
        proc = subprocess.run(
            snippet.command,
            shell=True,
            capture_output=True,
            text=True,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def export_snippets(self) -> list[dict]:
        return [s.to_dict() for s in self.db.get_all()]

    def import_snippets(self, data: list[dict], overwrite: bool = False) -> int:
        existing = {s.title: s for s in self.db.get_all()}
        imported_count = 0

        for item in data:
            snippet = Snippet.from_dict(item)
            if snippet.title in existing:
                if overwrite:
                    snippet.id = existing[snippet.title].id
                    self.db.update(snippet)
                    imported_count += 1
            else:
                self.db.insert(snippet)
                imported_count += 1

        return imported_count

    def get_stats(self) -> dict:
        snippets = self.db.get_all()
        tag_counts: dict[str, int] = {}
        for s in snippets:
            for t in s.tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1

        most_used = sorted(snippets, key=lambda s: s.times_used, reverse=True)[:5]
        return {
            "total_snippets": len(snippets),
            "total_tags": len(tag_counts),
            "top_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_used": [{"id": s.id, "title": s.title, "uses": s.times_used} for s in most_used],
        }
