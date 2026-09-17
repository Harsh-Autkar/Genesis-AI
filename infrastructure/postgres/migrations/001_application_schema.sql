CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY,
    owner_user_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS papers (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_papers_project_id
    ON papers(project_id);

CREATE TABLE IF NOT EXISTS paper_versions (
    id UUID PRIMARY KEY,
    paper_id UUID NOT NULL REFERENCES papers(id),
    version_number INTEGER NOT NULL,
    storage_key TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    processing_status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_paper_versions_paper_version
        UNIQUE (paper_id, version_number),

    CONSTRAINT ck_paper_versions_version_positive
        CHECK (version_number > 0),

    CONSTRAINT ck_paper_versions_file_size_nonnegative
        CHECK (file_size >= 0)
);

CREATE INDEX IF NOT EXISTS idx_paper_versions_paper_id
    ON paper_versions(paper_id);

CREATE TABLE IF NOT EXISTS processing_jobs (
    id UUID PRIMARY KEY,
    paper_version_id UUID NOT NULL
        REFERENCES paper_versions(id),

    job_type TEXT NOT NULL,
    status TEXT NOT NULL,
    stage TEXT,

    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,

    idempotency_key TEXT,
    pipeline_version TEXT NOT NULL,

    error_code TEXT,
    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    CONSTRAINT ck_processing_jobs_attempts_nonnegative
        CHECK (attempts >= 0),

    CONSTRAINT ck_processing_jobs_max_attempts_positive
        CHECK (max_attempts > 0)
);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_status_created
    ON processing_jobs(status, created_at);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_paper_version
    ON processing_jobs(paper_version_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_processing_jobs_idempotency
    ON processing_jobs(idempotency_key)
    WHERE idempotency_key IS NOT NULL;