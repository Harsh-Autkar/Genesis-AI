from io import BytesIO
from uuid import uuid4

from services.persistence.projects import ProjectRepository

from apps.api.app.services.paper_upload import PaperUploadService


class FakeUpload:
    def __init__(
        self,
        *,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> None:
        self.filename = filename
        self.content_type = content_type
        self.file = BytesIO(content)


def test_paper_upload_service_persists_paper_version_and_job():
    project_id = uuid4()

    ProjectRepository().create(project_id=project_id)

    upload = FakeUpload(
        filename="research-paper.pdf",
        content_type="application/pdf",
        content=b"%PDF-1.4\nGenesis-AI test document",
    )

    service = PaperUploadService()

    paper, paper_version, job, stored_file = service.upload(
        project_id=project_id,
        file=upload,
    )

    assert paper.project_id == project_id
    assert paper_version.paper_id == paper.id
    assert paper_version.version_number == 1
    assert paper_version.processing_status == "QUEUED"

    assert job.paper_version_id == paper_version.id
    assert job.status == "QUEUED"
    assert job.stage == "VALIDATING"
    assert job.pipeline_version == "1.0.0"

    assert stored_file.storage_key.endswith("/original.pdf")
    assert stored_file.size_bytes > 0