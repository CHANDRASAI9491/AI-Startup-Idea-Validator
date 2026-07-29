import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "AI Startup Idea Validator"


def test_validate_api():
    payload = {
        "idea_text": "AI-powered automated tax advisory tool for freelancers",
        "target_industry": "FinTech",
        "target_audience": "Freelancers & Contractors",
        "session_id": "test_api_session"
    }
    response = client.post("/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["overall_score"] is not None


def test_get_report_api():
    response = client.get("/report/test_api_session")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_advisor_api():
    payload = {
        "session_id": "test_api_session",
        "question": "What is the recommended pricing strategy?",
        "chat_history": []
    }
    response = client.post("/advisor", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 10
