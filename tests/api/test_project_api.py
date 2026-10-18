from fastapi.testclient import TestClient

from apps.api.app.main import app
from services.persistence.projects import ProjectRepository


client = TestClient(app)


def test_create_project():
    response = client.post("/api/v1/projects")

    assert response.status_code == 201

    body = response.json()

    assert "project_id" in body
    assert body["status"] == "CREATED"

    repository = ProjectRepository()

    project = repository.get_by_id(body["project_id"])

    assert project is not None