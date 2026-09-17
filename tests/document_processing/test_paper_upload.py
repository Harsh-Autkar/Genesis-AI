from io import BytesIO

from fastapi.testclient import TestClient

from apps.api.app.main import app


client = TestClient(app)


def create_test_project() -> str:
    response = client.post("/api/v1/projects")

    assert response.status_code == 201

    return response.json()["project_id"]


def test_valid_pdf_upload_is_accepted():
    project_id = create_test_project()

    response = client.post(
        f"/api/v1/projects/{project_id}/papers",
        files={
            "file": (
                "research-paper.pdf",
                BytesIO(b"%PDF-1.7\nminimal test content"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 202

    data = response.json()

    assert data["project_id"] == project_id
    assert data["filename"] == "research-paper.pdf"
    assert data["size_bytes"] > 0
    assert data["status"] == "QUEUED"
    assert data["paper_version_id"]
    assert data["sha256"]
    assert data["storage_key"].endswith("/original.pdf")
    assert data["content_type"] == "application/pdf"
    assert data["paper_id"]
    assert data["job_id"]


def test_non_pdf_upload_is_rejected():
    project_id = create_test_project()

    response = client.post(
        f"/api/v1/projects/{project_id}/papers",
        files={
            "file": (
                "research-paper.docx",
                BytesIO(b"not a pdf"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["error"]["code"] == "UNSUPPORTED_FILE"


def test_wrong_content_type_is_rejected():
    project_id = create_test_project()

    response = client.post(
        f"/api/v1/projects/{project_id}/papers",
        files={
            "file": (
                "research-paper.pdf",
                BytesIO(b"not really a pdf"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["error"]["code"] == "INVALID_CONTENT_TYPE"


def test_empty_upload_is_rejected():
    project_id = create_test_project()

    response = client.post(
        f"/api/v1/projects/{project_id}/papers",
        files={
            "file": (
                "research-paper.pdf",
                BytesIO(b""),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["error"]["code"] == "EMPTY_FILE"


def test_upload_over_15_mb_is_rejected():
    project_id = create_test_project()

    oversized_content = b"x" * (15 * 1024 * 1024 + 1)

    response = client.post(
        f"/api/v1/projects/{project_id}/papers",
        files={
            "file": (
                "research-paper.pdf",
                BytesIO(oversized_content),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["error"]["code"] == "FILE_TOO_LARGE"