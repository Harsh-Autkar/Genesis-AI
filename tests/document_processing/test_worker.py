from pathlib import Path
from uuid import uuid4

from services.document_processing.pipeline.interface import PipelineResult
from services.document_processing.worker.worker import (
    DocumentProcessingWorker,
)

from services.document_processing.chunks.interface import DocumentChunk
from services.document_processing.structure import SectionType


class FakeJob:
    def __init__(self):
        self.id = uuid4()
        self.paper_version_id = uuid4()
        self.pipeline_version = "1.0.0"


class FakePaperVersion:
    def __init__(self):
        self.id = uuid4()
        self.storage_key = "projects/test/paper/original.pdf"


class FakeJobRepository:
    def __init__(self, job):
        self.job = job
        self.succeeded_job_id = None

    def claim_next_queued_job(self):
        return self.job

    def mark_succeeded(self, job_id):
        self.succeeded_job_id = job_id
        return self.job


class FakePaperVersionRepository:
    def __init__(self, paper_version):
        self.paper_version = paper_version

    def get_by_id(self, version_id):
        assert version_id == self.paper_version.id
        return self.paper_version

class FakePaperChunkRepository:
    def __init__(self):
        self.created_chunks = None

    def create_many(self, *, chunks):
        self.created_chunks = chunks
        return ()

class FakePipeline:
    def __init__(self):
        self.received_storage_key = None

    def run(self, storage_key):
        self.received_storage_key = storage_key

        return PipelineResult(
            structured_document=None,
            scholarly_document=None,
            chunks=(),
            embeddings=(),
        )


def test_worker_processes_claimed_job():
    job = FakeJob()
    paper_version = FakePaperVersion()
    paper_chunk_repository = FakePaperChunkRepository()

    # Keep IDs aligned so the worker must resolve
    # the PaperVersion from the ProcessingJob.
    paper_version.id = job.paper_version_id

    job_repository = FakeJobRepository(job)
    paper_version_repository = FakePaperVersionRepository(
        paper_version
    )
    paper_chunk_repository = FakePaperChunkRepository()
    pipeline = FakePipeline()

    worker = DocumentProcessingWorker(
        job_repository=job_repository,
        paper_version_repository=paper_version_repository,
        pipeline=pipeline,
        paper_chunk_repository=paper_chunk_repository,
    )

    result = worker.run_once()

    assert result is not None
    assert pipeline.received_storage_key == paper_version.storage_key
    assert job_repository.succeeded_job_id == job.id


def test_worker_returns_none_when_no_job_is_available():
    class EmptyJobRepository:
        def claim_next_queued_job(self):
            return None

    job_repository = EmptyJobRepository()
    paper_version_repository = FakePaperVersionRepository(None)
    paper_chunk_repository = FakePaperChunkRepository()
    pipeline = FakePipeline()

    worker = DocumentProcessingWorker(
        job_repository=job_repository,
        paper_version_repository=paper_version_repository,
        paper_chunk_repository=paper_chunk_repository,
        pipeline=pipeline,
    )

    result = worker.run_once()

    assert result is None
    
def test_worker_retries_when_pipeline_fails():
    job = FakeJob()
    paper_version = FakePaperVersion()
    paper_chunk_repository = FakePaperChunkRepository()
    paper_version.id = job.paper_version_id

    class FailingPipeline:
        def run(self, storage_key):
            raise RuntimeError("pipeline failed")

    class RetryTrackingJobRepository(FakeJobRepository):
        def __init__(self, job):
            super().__init__(job)
            self.retry_args = None

        def retry(
            self,
            job_id,
            *,
            error_code,
            error_message,
        ):
            self.retry_args = (
                job_id,
                error_code,
                error_message,
            )
            return self.job

    job_repository = RetryTrackingJobRepository(job)

    paper_version_repository = FakePaperVersionRepository(
        paper_version
    )

    worker = DocumentProcessingWorker(
        job_repository=job_repository,
        paper_version_repository=paper_version_repository,
        paper_chunk_repository=paper_chunk_repository,
        pipeline=FailingPipeline(),
    )

    result = worker.run_once()

    assert result is None
    assert job_repository.retry_args is not None

    job_id, error_code, error_message = job_repository.retry_args

    assert job_id == job.id
    assert error_code == "PIPELINE_ERROR"
    assert error_message == "pipeline failed"
    
def test_worker_fails_when_paper_version_is_missing():
    job = FakeJob()
    paper_chunk_repository = FakePaperChunkRepository()

    class MissingPaperVersionRepository:
        def get_by_id(self, version_id):
            assert version_id == job.paper_version_id
            return None

    class TrackingJobRepository(FakeJobRepository):
        def __init__(self, job):
            super().__init__(job)
            self.failure_args = None

        def mark_failed(
            self,
            job_id,
            *,
            error_code,
            error_message,
        ):
            self.failure_args = (
                job_id,
                error_code,
                error_message,
            )
            return self.job

    job_repository = TrackingJobRepository(job)

    worker = DocumentProcessingWorker(
    job_repository=job_repository,
    paper_version_repository=MissingPaperVersionRepository(),
    paper_chunk_repository=paper_chunk_repository,
    pipeline=None,
)

    result = worker.run_once()

    assert result is None
    assert job_repository.failure_args is not None

    job_id, error_code, error_message = job_repository.failure_args

    assert job_id == job.id
    assert error_code == "PAPER_VERSION_NOT_FOUND"
    assert str(job.paper_version_id) in error_message
    
def test_worker_persists_pipeline_chunks_before_succeeding():
    job = FakeJob()
    paper_version = FakePaperVersion()
    paper_version.id = job.paper_version_id

    class TrackingPaperChunkRepository:
        def __init__(self):
            self.created_chunks = None

        def create_many(self, *, chunks):
            self.created_chunks = chunks
            return ()

    class ChunkProducingPipeline:
        def run(self, storage_key):
            return PipelineResult(
                structured_document=None,
                scholarly_document=None,
                chunks=(
                    DocumentChunk(
                        chunk_id=str(uuid4()),
                        text="First chunk",
                        section_type=SectionType.ABSTRACT,
                        start_page=1,
                        end_page=1,
                        position=1,
                    ),
                    DocumentChunk(
                        chunk_id=str(uuid4()),
                        text="Second chunk",
                        section_type=SectionType.INTRODUCTION,
                        start_page=2,
                        end_page=2,
                        position=2,
                    ),
                ),
                embeddings=(),
            )

    class TrackingJobRepository(FakeJobRepository):
        pass

    job_repository = TrackingJobRepository(job)
    paper_version_repository = FakePaperVersionRepository(
        paper_version
    )
    chunk_repository = TrackingPaperChunkRepository()

    worker = DocumentProcessingWorker(
        job_repository=job_repository,
        paper_version_repository=paper_version_repository,
        paper_chunk_repository=chunk_repository,
        pipeline=ChunkProducingPipeline(),
    )

    result = worker.run_once()

    assert result is not None
    assert chunk_repository.created_chunks is not None
    assert len(chunk_repository.created_chunks) == 2

    assert chunk_repository.created_chunks[0]["paper_version_id"] == (
        paper_version.id
    )
    assert chunk_repository.created_chunks[0]["text"] == "First chunk"
    assert chunk_repository.created_chunks[0]["section_type"] == "abstract"    
    assert chunk_repository.created_chunks[0]["position"] == 1

    assert job_repository.succeeded_job_id == job.id
    
    
def test_worker_retries_when_chunk_persistence_fails():
    job = FakeJob()
    paper_version = FakePaperVersion()
    paper_version.id = job.paper_version_id

    class FailingPaperChunkRepository:
        def create_many(self, *, chunks):
            raise RuntimeError("chunk persistence failed")

    class ChunkProducingPipeline:
        def run(self, storage_key):
            return PipelineResult(
                structured_document=None,
                scholarly_document=None,
                chunks=(
                    DocumentChunk(
                        chunk_id=str(uuid4()),
                        text="First chunk",
                        section_type=SectionType.ABSTRACT,
                        start_page=1,
                        end_page=1,
                        position=1,
                    ),
                ),
                embeddings=(),
            )

    class RetryTrackingJobRepository(FakeJobRepository):
        def __init__(self, job):
            super().__init__(job)
            self.retry_args = None

        def retry(
            self,
            job_id,
            *,
            error_code,
            error_message,
        ):
            self.retry_args = (
                job_id,
                error_code,
                error_message,
            )
            return self.job

    job_repository = RetryTrackingJobRepository(job)

    worker = DocumentProcessingWorker(
        job_repository=job_repository,
        paper_version_repository=FakePaperVersionRepository(
            paper_version
        ),
        paper_chunk_repository=FailingPaperChunkRepository(),
        pipeline=ChunkProducingPipeline(),
    )

    result = worker.run_once()

    assert result is None
    assert job_repository.retry_args is not None

    job_id, error_code, error_message = job_repository.retry_args

    assert job_id == job.id
    assert error_code == "OUTPUT_PERSISTENCE_ERROR"
    assert error_message == "chunk persistence failed"
    assert job_repository.succeeded_job_id is None