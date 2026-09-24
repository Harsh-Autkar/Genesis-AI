BEGIN;

-- Keep the newest embedding for each logical
-- source/model/version combination.
DELETE FROM embeddings
WHERE id IN (
    SELECT id
    FROM (
        SELECT
            id,
            ROW_NUMBER() OVER (
                PARTITION BY
                    source_type,
                    source_id,
                    model_name,
                    model_version
                ORDER BY created_at DESC, id DESC
            ) AS rn
        FROM embeddings
    ) ranked
    WHERE rn > 1
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'uq_embeddings_source_model'
    ) THEN
        ALTER TABLE embeddings
            ADD CONSTRAINT uq_embeddings_source_model
            UNIQUE (
                source_type,
                source_id,
                model_name,
                model_version
            );
    END IF;
END
$$;

COMMIT;
