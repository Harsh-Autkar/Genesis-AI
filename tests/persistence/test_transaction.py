from uuid import uuid4

import pytest

from services.persistence.database import transaction
from services.persistence.paper_versions import PaperVersionRepository
from services.persistence.papers import PaperRepository
from services.persistence.processing_jobs import ProcessingJobRepository
from services.persistence.projects import ProjectRepository


def test_related_records_commit_as_one_transaction():
    project_id = uuid4()
    paper_id = uuid4()
    version_id = uuid4()
    job_id = uuid4()

    project_repository = ProjectRepository()
    paper_repository = PaperRepository()
    version_repository = PaperVersionRepository()
    job_repository = ProcessingJobRepository()

    with transaction() as connection:
        project_repository.create(
            project_id=project_id,
            connection=connection,
        )

        paper_repository.create(
            paper_id=paper_id,
            project_id=project_id,
            connection=connection,
        )

        version_repository.create(
            version_id=version_id,
            paper_id=paper_id,
            version_number=1,
            storage_key="transaction-test/original.pdf",
            file_hash="transaction-test-hash",
            file_size=1024,
            mime_type="application/pdf",
            processing_status="QUEUED",
            connection=connection,
        )

        job_repository.create(
            job_id=job_id,
            paper_version_id=version_id,
            job_type="PAPER_ANALYSIS",
            status="QUEUED",
            pipeline_version="1.0.0",
            connection=connection,
        )

    assert project_repository.get_by_id(project_id) is not None
    assert paper_repository.get_by_id(paper_id) is not None
    assert version_repository.get_by_id(version_id) is not None
    assert job_repository.get_by_id(job_id) is not None


def test_transaction_rolls_back_all_related_records():
    project_id = uuid4()
    paper_id = uuid4()
    version_id = uuid4()
    job_id = uuid4()

    project_repository = ProjectRepository()
    paper_repository = PaperRepository()
    version_repository = PaperVersionRepository()
    job_repository = ProcessingJobRepository()

    with pytest.raises(RuntimeError, match="forced rollback"):
        with transaction() as connection:
            project_repository.create(
                project_id=project_id,
                connection=connection,
            )

            paper_repository.create(
                paper_id=paper_id,
                project_id=project_id,
                connection=connection,
            )

            version_repository.create(
                version_id=version_id,
                paper_id=paper_id,
                version_number=1,
                storage_key="transaction-test/rollback.pdf",
                file_hash="rollback-test-hash",
                file_size=1024,
                mime_type="application/pdf",
                processing_status="QUEUED",
                connection=connection,
            )

            job_repository.create(
                job_id=job_id,
                paper_version_id=version_id,
                job_type="PAPER_ANALYSIS",
                status="QUEUED",
                pipeline_version="1.0.0",
                connection=connection,
            )

            raise RuntimeError("forced rollback")

    assert project_repository.get_by_id(project_id) is None
    assert paper_repository.get_by_id(paper_id) is None
    assert version_repository.get_by_id(version_id) is None
    assert job_repository.get_by_id(job_id) is None