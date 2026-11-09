"""Opt-in integration tests: DZN_AI_TEST_DATABASE_URL must point to disposable Postgres."""
import os

import psycopg
import pytest

from delnavazan_ai import migrate

TEST_URL = os.environ.get("DZN_AI_TEST_DATABASE_URL", "")
pytestmark = pytest.mark.skipif(not TEST_URL, reason="No disposable Postgres URL configured")


def test_migrations_idempotent(monkeypatch) -> None:
    monkeypatch.setattr(migrate, "connect", lambda: psycopg.connect(TEST_URL))
    assert migrate.apply_migrations() == ["001_initial.sql", "002_jobs.sql"]
    assert migrate.apply_migrations() == []


def test_job_claim_and_dead_letter(monkeypatch) -> None:
    from delnavazan_ai import worker

    monkeypatch.setattr(worker, "connect", lambda: psycopg.connect(TEST_URL))
    with psycopg.connect(TEST_URL) as conn:
        conn.execute("DELETE FROM jobs")
        conn.execute(
            "INSERT INTO jobs(kind, idempotency_key, max_attempts) VALUES (%s, %s, %s)",
            ("unsupported", "integration-job", 1),
        )
        conn.commit()
        assert worker.process_one(conn)
        assert conn.execute("SELECT state FROM jobs").fetchone()[0] == "dead"
