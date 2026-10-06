import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_api_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "openai_configured" in data
    assert "model" in data

def test_start_research_session():
    response = client.post(
        "/api/research/start",
        json={"question": "What are the latest benchmarks for solid-state batteries in 2025?", "deep_mode": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "planning"
    assert "stream_url" in data

def test_list_and_get_sessions():
    # Start a research session to ensure there's at least one in DB
    start_resp = client.post(
        "/api/research/start",
        json={"question": "What is the status of sodium-ion battery deployment?", "deep_mode": False}
    )
    session_id = start_resp.json()["session_id"]

    # List sessions
    list_resp = client.get("/api/research/sessions")
    assert list_resp.status_code == 200
    sessions = list_resp.json()
    assert isinstance(sessions, list)
    assert any(s["session_id"] == session_id for s in sessions)

    # Get specific session
    get_resp = client.get(f"/api/research/sessions/{session_id}")
    assert get_resp.status_code == 200
    session_data = get_resp.json()
    assert session_data["session_id"] == session_id

def test_get_nonexistent_session_404():
    response = client.get("/api/research/sessions/nonexistent-id-999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Research session not found"

def test_start_research_validation_error():
    # Question too short (less than 5 characters)
    response = client.post(
        "/api/research/start",
        json={"question": "Why", "deep_mode": False}
    )
    assert response.status_code == 422 # Unprocessable Entity
