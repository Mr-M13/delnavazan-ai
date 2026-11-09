"""Versioned, explicitly approved public knowledge retrieval.

No automatic publication of scraped WordPress pages or internal content.
"""
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeEntry:
    id: str
    title: str
    text: str
    source_url: str
    version: int
    approved: bool
    effective_from: date
    effective_until: date | None
    tags: tuple[str, ...]


def _words(value: str) -> set[str]:
    return set(re.findall(r"[\w\u0600-\u06ff]+", value.casefold(), flags=re.UNICODE))


def load_approved(path: Path, today: date | None = None) -> list[KnowledgeEntry]:
    today = today or date.today()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("Unsupported knowledge schema")
    entries: list[KnowledgeEntry] = []
    seen: set[str] = set()
    for item in payload.get("entries", []):
        identifier = item["id"]
        if identifier in seen:
            raise ValueError("Duplicate knowledge identifier")
        seen.add(identifier)
        if item.get("status") != "approved" or not item.get("approved_by"):
            continue
        if not item.get("source_url", "").startswith("https://"):
            continue
        start = date.fromisoformat(item["effective_from"])
        end = date.fromisoformat(item["effective_until"]) if item.get("effective_until") else None
        if start > today or (end is not None and end < today):
            continue
        entries.append(
            KnowledgeEntry(
                id=identifier,
                title=item["title"],
                text=item["text"],
                source_url=item["source_url"],
                version=int(item["version"]),
                approved=True,
                effective_from=start,
                effective_until=end,
                tags=tuple(item.get("tags", [])),
            )
        )
    return entries


def retrieve(query: str, entries: list[KnowledgeEntry], limit: int = 3) -> list[KnowledgeEntry]:
    if not query.strip() or limit <= 0:
        return []
    terms = _words(query)
    scored = []
    for entry in entries:
        title_terms = _words(entry.title + " " + " ".join(entry.tags))
        content_terms = _words(entry.text)
        score = len(terms & title_terms) * 3 + len(terms & content_terms)
        if score:
            scored.append((score, entry))
    scored.sort(key=lambda row: (-row[0], row[1].id))
    return [entry for _, entry in scored[:limit]]
