import json
import logging

from delnavazan_ai.logging_config import JsonFormatter


def test_json_log_has_expected_fields() -> None:
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "worker_started", (), None)
    parsed = json.loads(JsonFormatter().format(record))
    assert parsed["event"] == "worker_started"
    assert parsed["level"] == "INFO"
    assert parsed["timestamp"].endswith("+00:00")
