"""Apply numbered SQL migrations under a PostgreSQL advisory lock."""
from pathlib import Path

from .database import connect

MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"
LOCK_ID = 91374011


def apply_migrations() -> list[str]:
    applied = []
    with connect() as conn:
        conn.execute("SELECT pg_advisory_lock(%s)", (LOCK_ID,))
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations "
                "(name TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"
            )
            conn.commit()
            for path in sorted(MIGRATIONS.glob("[0-9]*.sql")):
                with conn.transaction():
                    row = conn.execute(
                        "SELECT 1 FROM schema_migrations WHERE name=%s", (path.name,)
                    ).fetchone()
                    if row:
                        continue
                    conn.execute(path.read_text(encoding="utf-8"))
                    conn.execute(
                        "INSERT INTO schema_migrations(name) VALUES (%s)", (path.name,)
                    )
                    applied.append(path.name)
        finally:
            conn.rollback()
            conn.execute("SELECT pg_advisory_unlock(%s)", (LOCK_ID,))
            conn.commit()
    return applied


if __name__ == "__main__":
    print("Applied:", ", ".join(apply_migrations()) or "none")
