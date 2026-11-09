"""Durable internal job runner. External communication handlers are not registered."""
import logging
import signal
import threading
import uuid

from .database import connect
from .logging_config import configure_logging

HANDLERS = {}
logger = logging.getLogger(__name__)


def claim_job(conn):
    token = uuid.uuid4()
    with conn.transaction():
        return conn.execute(
            """WITH candidate AS (
                SELECT id FROM jobs
                WHERE (state='pending' AND available_at <= NOW())
                   OR (state='leased' AND leased_until < NOW())
                ORDER BY available_at, id FOR UPDATE SKIP LOCKED LIMIT 1
            )
            UPDATE jobs SET state='leased', attempts=attempts+1,
                leased_until=NOW()+INTERVAL '60 seconds', claim_token=%s
            WHERE id=(SELECT id FROM candidate)
            RETURNING id, kind, payload, attempts, max_attempts, claim_token""",
            (token,),
        ).fetchone()


def process_one(conn) -> bool:
    job = claim_job(conn)
    if job is None:
        return False
    conn.commit()
    job_id, kind, payload, attempts, max_attempts, claim_token = job
    logger.info("job_claimed id=%s kind=%s", job_id, kind)
    try:
        if kind not in HANDLERS:
            raise ValueError("Unregistered job type")
        HANDLERS[kind](payload)
    except Exception:  # noqa: BLE001 - quarantine all job handler failures
        logger.warning("job_handler_failed id=%s kind=%s", job_id, kind)
        if attempts >= max_attempts:
            conn.execute(
                "UPDATE jobs SET state='dead', leased_until=NULL, last_error=%s "
                "WHERE id=%s AND state='leased' AND claim_token=%s",
                ("job_failed", job_id, claim_token),
            )
        else:
            delay = min(3600, 2 ** min(attempts, 10))
            conn.execute(
                "UPDATE jobs SET state='pending', leased_until=NULL, "
                "available_at=NOW()+(%s * INTERVAL '1 second'), last_error=%s "
                "WHERE id=%s AND state='leased' AND claim_token=%s",
                (delay, "job_failed", job_id, claim_token),
            )
    else:
        logger.info("job_completed id=%s", job_id)
        conn.execute(
            "UPDATE jobs SET state='done', leased_until=NULL "
            "WHERE id=%s AND state='leased' AND claim_token=%s",
            (job_id, claim_token),
        )
    conn.commit()
    return True


def run(stop: threading.Event) -> None:
    with connect() as conn:
        while not stop.is_set():
            if not process_one(conn):
                stop.wait(2)


def main() -> None:
    configure_logging()
    stop = threading.Event()

    def shutdown(_signum, _frame) -> None:
        logger.info("worker_shutdown_requested")
        stop.set()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    run(stop)


if __name__ == "__main__":
    main()
