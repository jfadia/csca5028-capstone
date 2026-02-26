import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
import app


class MockResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code

    @staticmethod
    def json():
        return {
            "Data": [
                {"TIMESTAMP": 1700000000, "CLOSE": 50000},
                {"TIMESTAMP": 1700086400, "CLOSE": 51000},
            ]
        }


@pytest.fixture
def client():
    print("Setting up the test environment...")
    with TestClient(app.app) as client:
        yield client


def test_app_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("requests.get", return_value=MockResponse())
@patch("app.insert_prices")
@patch("app.truncate_prices")
def test_app_collect_data(mock_truncate, mock_insert, mock_get, client):
    params = {"start_date": "2024-01-01", "end_date": "2024-01-02"}
    response = client.get("/data", params=params)
    assert response.status_code == 200
    mock_get.assert_called_once()
    mock_truncate.assert_called_once()
    mock_insert.assert_called_once()
