"""Database connectivity with bounded timeouts."""
import psycopg

from .settings import settings


def connect():
    if not settings.database_url:
        raise RuntimeError("Database URL is not configured")
    return psycopg.connect(settings.database_url, connect_timeout=3)


def is_ready() -> bool:
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
        return True
    except (psycopg.Error, RuntimeError):
        return False
