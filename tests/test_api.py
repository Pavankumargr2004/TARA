"""
Smoke tests for the FastAPI endpoints.
"""
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]


def test_list_threats():
    response = client.get("/api/v1/threats")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_threat_not_found():
    response = client.get("/api/v1/threats/NONEXISTENT")
    assert response.status_code == 404


def test_list_audits():
    response = client.get("/api/v1/audit")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
