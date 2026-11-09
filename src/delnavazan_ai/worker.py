"""Durable internal job runner. External communication handlers are not registered."""
import time

from .database import connect

HANDLERS = {}


def claim_job(conn):
    with conn.transaction():
        return conn.execute(
            """WITH candidate AS (
                SELECT id FROM jobs
                WHERE (state='pending' AND available_at <= NOW())
                   OR (state='leased' AND leased_until < NOW())
                ORDER BY available_at, id FOR UPDATE SKIP LOCKED LIMIT 1
            )
            UPDATE jobs SET state='leased', attempts=attempts+1,
                leased_until=NOW()+INTERVAL '60 seconds'
            WHERE id=(SELECT id FROM candidate)
            RETURNING id, kind, payload, attempts, max_attempts""",
        ).fetchone()


def process_one(conn) -> bool:
    job = claim_job(conn)
    if job is None:
        return False
    job_id, kind, payload, attempts, max_attempts = job
    try:
        if kind not in HANDLERS:
            raise ValueError("Unregistered job type")
        HANDLERS[kind](payload)
    except Exception:  # noqa: BLE001 - job boundary must quarantine all handler failures
        # Never persist exception text: provider errors may contain sensitive content.
        if attempts >= max_attempts:
            conn.execute(
                "UPDATE jobs SET state='dead', leased_until=NULL, last_error=%s "
                "WHERE id=%s",
                ("job_failed", job_id),
            )
        else:
            delay = min(3600, 2 ** min(attempts, 10))
            conn.execute(
                "UPDATE jobs SET state='pending', leased_until=NULL, "
                "available_at=NOW()+(%s * INTERVAL '1 second'), last_error=%s "
                "WHERE id=%s",
                (delay, "job_failed", job_id),
            )
    else:
        conn.execute(
            "UPDATE jobs SET state='done', leased_until=NULL WHERE id=%s", (job_id,)
        )
    conn.commit()
    return True


def main() -> None:
    with connect() as conn:
        while True:
            if not process_one(conn):
                time.sleep(2)


if __name__ == "__main__":
    main()
