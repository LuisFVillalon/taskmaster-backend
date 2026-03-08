import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_create_task_with_all_fields():
    task_data = {
        "title": "Full Task",
        "description": "Complete backend migration",
        "category": "test",
        "completed": false,
        "urgent": true,
        "due_date": "2026-03-31",
        "due_time": "17:00:00",
        "estimated_time": 4,
        "complexity": 4,
        "parent_task_id": null,
        "user_id": 1,
        "tags": []
}

    response = client.post("/create-task", json=task_data)

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Full Task"
    assert data["estimated_time"] == 8.5
    assert data["complexity"] == 4
    assert data["user_id"] == 1