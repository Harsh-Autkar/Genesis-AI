from unittest import result

from services.document_processing.pipeline.interface import PipelineResult
from services.document_processing.pipeline.pipeline import (
    DefaultDocumentProcessingPipeline,
)
from services.persistence.paper_versions import PaperVersionRepository
from services.persistence.processing_jobs import (
    ProcessingJobRepository,
)


class DocumentProcessingWorker:
    """Execute one queued document-processing job."""

    def __init__(
        self,
        *,
        job_repository: ProcessingJobRepository,
        paper_version_repository: PaperVersionRepository,
        pipeline: DefaultDocumentProcessingPipeline,
    ) -> None:
        self.job_repository = job_repository
        self.paper_version_repository = paper_version_repository
        self.pipeline = pipeline

    def run_once(self) -> PipelineResult | None:
        """Claim and execute one queued processing job."""

        job = self.job_repository.claim_next_queued_job()

        if job is None:
            return None

        paper_version = self.paper_version_repository.get_by_id(
            job.paper_version_id
        )

        if paper_version is None:
            self.job_repository.mark_failed(
                job.id,
                error_code="PAPER_VERSION_NOT_FOUND",
                error_message=(
                    f"Paper version '{job.paper_version_id}' "
                    "does not exist."
                ),
            )
            return None

        try:
            result = self.pipeline.run(
                paper_version.storage_key
            )
        except Exception as exc:
            self.job_repository.retry(
                job.id,
                error_code="PIPELINE_ERROR",
                error_message=str(exc),
            )
            return None

        self.job_repository.mark_succeeded(job.id)

        return result