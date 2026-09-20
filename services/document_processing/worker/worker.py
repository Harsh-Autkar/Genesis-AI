from services.document_processing.pipeline.interface import PipelineResult
from services.document_processing.pipeline.pipeline import (
    DefaultDocumentProcessingPipeline,
)
from services.persistence.paper_chunks import PaperChunkRepository
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
        paper_chunk_repository: PaperChunkRepository,
        pipeline: DefaultDocumentProcessingPipeline,
    ) -> None:
        self.job_repository = job_repository
        self.paper_version_repository = paper_version_repository
        self.paper_chunk_repository = paper_chunk_repository
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

        try:
            self.paper_chunk_repository.create_many(
                chunks=self._build_chunk_records(
                    result=result,
                    paper_version_id=paper_version.id,
                    pipeline_version=job.pipeline_version,
                )
            )
        except Exception as exc:
            self.job_repository.retry(
                job.id,
                error_code="OUTPUT_PERSISTENCE_ERROR",
                error_message=str(exc),
            )
            return None

        self.job_repository.mark_succeeded(job.id)

        return result

    @staticmethod
    def _build_chunk_records(
        *,
        result: PipelineResult,
        paper_version_id,
        pipeline_version: str,
    ) -> list[dict]:
        return [
            {
                "id": __import__("uuid").UUID(chunk.chunk_id),
                "paper_version_id": paper_version_id,
                "text": chunk.text,
                "section_type": chunk.section_type.value,
                "start_page": chunk.start_page,
                "end_page": chunk.end_page,
                "position": chunk.position,
                "pipeline_version": pipeline_version,
            }
            for chunk in result.chunks
        ]