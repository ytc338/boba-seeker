import os
import sys

from fastapi.testclient import TestClient

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)


def test_create_feedback():
    response = client.post(
        "/api/feedback",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "message": "This is a test message",
            "type": "suggestion",
        },
    )
    assert response.status_code == 201, (
        f"Failed with status {response.status_code}: {response.text}"
    )

    data = response.json()
    assert data.get("status") in ["sent", "received"], (
        f"Unexpected status: {data.get('status')}"
    )
