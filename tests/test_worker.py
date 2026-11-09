from unittest.mock import MagicMock

from delnavazan_ai.worker import process_one


def test_no_due_jobs() -> None:
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = None
    assert process_one(conn) is False


def test_unknown_job_retries_without_external_send() -> None:
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = (7, "send_whatsapp", {}, 1, 5)
    assert process_one(conn) is True
    assert conn.commit.call_count == 2


def test_unknown_job_exhausted_is_dead_lettered() -> None:
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = (7, "send_whatsapp", {}, 5, 5)
    assert process_one(conn) is True
    assert any("state='dead'" in str(call) for call in conn.execute.call_args_list)


def test_lease_committed_before_handler() -> None:
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = (9, "unregistered", {}, 1, 5)
    process_one(conn)
    assert conn.commit.call_count == 2
