from pathlib import Path
from uuid import UUID, uuid4

from services.document_processing.intake.stream import measure_stream_size
from services.document_processing.intake.validator import validate_document
from services.document_processing.storage.interface import FileStorage
from services.persistence.database import transaction
from services.persistence.paper_versions import PaperVersionRepository
from services.persistence.papers import PaperRepository
from services.persistence.processing_jobs import ProcessingJobRepository
from services.persistence.projects import ProjectRepository

from .storage import file_storage


PIPELINE_VERSION = "1.0.0"
JOB_TYPE = "PAPER_ANALYSIS"
JOB_STATUS = "QUEUED"
PAPER_VERSION_STATUS = "QUEUED"
JOB_STAGE = "VALIDATING"


class PaperUploadService:
    """Application service for accepting and registering a research paper."""

    def __init__(
        self,
        *,
        project_repository: ProjectRepository | None = None,
        paper_repository: PaperRepository | None = None,
        paper_version_repository: PaperVersionRepository | None = None,
        processing_job_repository: ProcessingJobRepository | None = None,
        storage: FileStorage | None = None,
    ) -> None:
        self.project_repository = project_repository or ProjectRepository()
        self.paper_repository = paper_repository or PaperRepository()
        self.paper_version_repository = (
            paper_version_repository or PaperVersionRepository()
        )
        self.processing_job_repository = (
            processing_job_repository or ProcessingJobRepository()
        )
        self.storage = storage or file_storage

    def upload(
        self,
        *,
        project_id: UUID,
        file,
    ):
        # 1. Validate the project before storing the artifact.
        project = self.project_repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError(project_id)

        # 2. Validate the uploaded document.
        try:
            size_bytes = measure_stream_size(file.file)
        except Exception as exc:
            raise PaperUploadValidationError(
                "FILE_TOO_LARGE",
                "The uploaded file exceeds the 15 MB limit.",
            ) from exc

        validation = validate_document(
            filename=file.filename or "",
            content_type=file.content_type or "",
            size_bytes=size_bytes,
        )

        if not validation.valid:
            raise PaperUploadValidationError(
                validation.error_code,
                validation.error_message,
            )

        # 3. Create domain identifiers.
        paper_id = uuid4()
        paper_version_id = uuid4()
        job_id = uuid4()

        extension = Path(validation.filename).suffix.lower()

        storage_key = (
            f"projects/{project_id}/"
            f"papers/{paper_id}/"
            f"versions/{paper_version_id}/"
            f"original{extension}"
        )

        # measure_stream_size consumes the stream, so rewind it before storing.
        file.file.seek(0)

        stored_file = None

        try:
            # 4. Persist the binary artifact first.
            stored_file = self.storage.store(
                file.file,
                storage_key=storage_key,
                content_type=validation.content_type,
            )

            # 5. Register all related records atomically.
            with transaction() as connection:
                paper = self.paper_repository.create(
                    paper_id=paper_id,
                    project_id=project_id,
                    connection=connection,
                )

                paper_version = self.paper_version_repository.create(
                    version_id=paper_version_id,
                    paper_id=paper.id,
                    version_number=1,
                    storage_key=stored_file.storage_key,
                    file_hash=stored_file.sha256,
                    file_size=stored_file.size_bytes,
                    mime_type=stored_file.content_type,
                    processing_status=PAPER_VERSION_STATUS,
                    connection=connection,
                )

                job = self.processing_job_repository.create(
                    job_id=job_id,
                    paper_version_id=paper_version.id,
                    job_type=JOB_TYPE,
                    status=JOB_STATUS,
                    stage=JOB_STAGE,
                    pipeline_version=PIPELINE_VERSION,
                    connection=connection,
                )

        except Exception:
            # PostgreSQL has rolled back at this point.
            # Compensate for the filesystem write.
            if stored_file is not None:
                self.storage.delete(storage_key=stored_file.storage_key)

            raise

        return paper, paper_version, job, stored_file


class ProjectNotFoundError(Exception):
    """Raised when a paper is uploaded to a non-existent project."""

    def __init__(self, project_id: UUID) -> None:
        super().__init__(f"Project '{project_id}' was not found.")
        self.project_id = project_id


class PaperUploadValidationError(Exception):
    """Raised when the uploaded document fails validation."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message