CREATE TABLE IF NOT EXISTS paper_chunks (
    id UUID PRIMARY KEY,
    paper_version_id UUID NOT NULL
        REFERENCES paper_versions(id),

    text TEXT NOT NULL,
    section_type TEXT NOT NULL,

    start_page INTEGER NOT NULL,
    end_page INTEGER NOT NULL,
    position INTEGER NOT NULL,

    pipeline_version TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_paper_chunks_start_page_positive
        CHECK (start_page > 0),

    CONSTRAINT ck_paper_chunks_end_page_positive
        CHECK (end_page > 0),

    CONSTRAINT ck_paper_chunks_page_range_valid
        CHECK (end_page >= start_page),

    CONSTRAINT ck_paper_chunks_position_nonnegative
        CHECK (position >= 0),

    CONSTRAINT uq_paper_chunks_position
        UNIQUE (
            paper_version_id,
            pipeline_version,
            position
        )
);

CREATE INDEX IF NOT EXISTS idx_paper_chunks_paper_version
    ON paper_chunks(paper_version_id);

CREATE INDEX IF NOT EXISTS idx_paper_chunks_paper_version_position
    ON paper_chunks(
        paper_version_id,
        pipeline_version,
        position
    );