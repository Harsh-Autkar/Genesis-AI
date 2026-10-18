from io import BytesIO

from fastapi.testclient import TestClient

from apps.api.app.main import app


client = TestClient(app)


def create_project() -> str:
    response = client.post("/api/v1/projects")

    assert response.status_code == 201

    return response.json()["project_id"]


def upload_paper(project_id: str) -> dict:
    response = client.post(
        f"/api/v1/projects/{project_id}/papers",
        files={
            "file": (
                "job-test.pdf",
                BytesIO(b"%PDF-1.7\nGenesis-AI job test"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 202

    return response.json()


def test_get_job_status():
    project_id = create_project()

    upload_data = upload_paper(project_id)
    job_id = upload_data["job_id"]

    response = client.get(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["paper_version_id"] == upload_data["paper_version_id"]
    assert data["job_type"] == "PAPER_ANALYSIS"
    assert data["status"] == "QUEUED"
    assert data["stage"] == "VALIDATING"
    assert data["attempts"] == 0
    assert data["max_attempts"] == 3
    assert data["pipeline_version"] == "1.0.0"


def test_get_unknown_job_returns_404():
    response = client.get(
        "/api/v1/jobs/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == "JOB_NOT_FOUND"