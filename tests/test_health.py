from unittest.mock import patch

from fastapi.testclient import TestClient

from delnavazan_ai.app import app


def test_liveness() -> None:
    response = TestClient(app).get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_without_database() -> None:
    with patch("delnavazan_ai.app.is_ready", return_value=False):
        response = TestClient(app).get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}


def test_readiness_with_database() -> None:
    with patch("delnavazan_ai.app.is_ready", return_value=True):
        response = TestClient(app).get("/health/ready")
    assert response.status_code == 200
