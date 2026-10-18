CREATE TABLE IF NOT EXISTS literature_items (
    id UUID PRIMARY KEY,

    provider TEXT NOT NULL,
    provider_id TEXT NOT NULL,

    title TEXT NOT NULL,
    abstract TEXT,

    publication_date DATE,
    venue TEXT,
    doi TEXT,

    source TEXT NOT NULL,

    domains TEXT[] NOT NULL DEFAULT '{}',
    topics TEXT[] NOT NULL DEFAULT '{}',

    access_status TEXT NOT NULL,
    full_text_location TEXT,

    processing_status TEXT NOT NULL,

    provenance_source TEXT NOT NULL,
    provenance_source_id TEXT NOT NULL,
    retrieved_at TIMESTAMPTZ NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_literature_provider_id
        UNIQUE (provider, provider_id),

    CONSTRAINT uq_literature_doi
        UNIQUE (doi)
);


CREATE TABLE IF NOT EXISTS literature_external_ids (
    id UUID PRIMARY KEY,

    literature_item_id UUID NOT NULL
        REFERENCES literature_items(id)
        ON DELETE CASCADE,

    provider TEXT NOT NULL,
    external_id TEXT NOT NULL,

    CONSTRAINT uq_literature_external_id
        UNIQUE (provider, external_id)
);


CREATE TABLE IF NOT EXISTS literature_authors (
    id UUID PRIMARY KEY,

    literature_item_id UUID NOT NULL
        REFERENCES literature_items(id)
        ON DELETE CASCADE,

    author_position INTEGER NOT NULL,
    name TEXT NOT NULL,
    provider_author_id TEXT,
    orcid TEXT,

    CONSTRAINT ck_literature_author_position_positive
        CHECK (author_position > 0),

    CONSTRAINT uq_literature_author_position
        UNIQUE (literature_item_id, author_position)
);


CREATE INDEX IF NOT EXISTS idx_literature_items_provider
    ON literature_items (provider);

CREATE INDEX IF NOT EXISTS idx_literature_items_publication_date
    ON literature_items (publication_date);

CREATE INDEX IF NOT EXISTS idx_literature_external_ids_item
    ON literature_external_ids (literature_item_id);

CREATE INDEX IF NOT EXISTS idx_literature_authors_item
    ON literature_authors (literature_item_id);