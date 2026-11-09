-- Internal durable jobs. No outbound handlers are enabled in AI-01.
CREATE TABLE IF NOT EXISTS jobs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kind TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    idempotency_key TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL DEFAULT 'pending'
        CHECK (state IN ('pending', 'leased', 'done', 'dead')),
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 5,
    available_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    leased_until TIMESTAMPTZ,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS jobs_due_idx ON jobs (available_at, id)
    WHERE state IN ('pending', 'leased');
