CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embeddings (
    id BIGSERIAL PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    vector vector(384) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_embeddings_source
    ON embeddings (source_type, source_id);

CREATE INDEX IF NOT EXISTS idx_embeddings_model
    ON embeddings (model_name, model_version);