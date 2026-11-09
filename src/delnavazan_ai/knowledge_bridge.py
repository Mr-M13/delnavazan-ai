"""Read-only bridge between approved public knowledge and the conversation engine."""
from datetime import date
from pathlib import Path

from .conversation import PublicFact, Reply, TextGenerator, reply_to_public_query
from .knowledge import load_approved, retrieve
from .settings import Settings


def answer_with_approved_knowledge(
    question: str,
    catalog: Path,
    generator: TextGenerator,
    config: Settings,
    today: date | None = None,
) -> Reply:
    entries = load_approved(catalog, today=today)
    matched = retrieve(question, entries)
    facts = [
        PublicFact(
            source_id=f"{entry.id}@v{entry.version}:{entry.source_url}",
            text=f"{entry.title}\n{entry.text}",
            approved=entry.approved,
        )
        for entry in matched
    ]
    return reply_to_public_query(question, facts, generator, config)
