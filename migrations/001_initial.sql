-- AI-01 baseline schema. Run on a dedicated database, never WordPress.
CREATE TABLE IF NOT EXISTS conversations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider VARCHAR(32) NOT NULL,
    provider_conversation_id TEXT NOT NULL,
    state VARCHAR(32) NOT NULL DEFAULT 'ai',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider, provider_conversation_id)
);
CREATE TABLE IF NOT EXISTS inbound_messages (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id),
    provider_message_id TEXT NOT NULL UNIQUE,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS staff (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chatwoot_user_id TEXT UNIQUE NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS roster_shifts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    staff_id BIGINT NOT NULL REFERENCES staff(id),
    weekday SMALLINT NOT NULL CHECK(weekday BETWEEN 0 AND 6),
    starts_at TIME NOT NULL,
    ends_at TIME NOT NULL,
    timezone TEXT NOT NULL DEFAULT 'Australia/Brisbane',
    priority INTEGER NOT NULL DEFAULT 100
);
CREATE TABLE IF NOT EXISTS escalations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id),
    assigned_staff_id BIGINT REFERENCES staff(id),
    state VARCHAR(32) NOT NULL DEFAULT 'unassigned',
    acknowledgement_deadline TIMESTAMPTZ,
    backup_deadline TIMESTAMPTZ,
    acknowledged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS notification_attempts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    escalation_id BIGINT NOT NULL REFERENCES escalations(id),
    channel VARCHAR(32) NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    attempted_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS audit_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id BIGINT REFERENCES conversations(id),
    event_type TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
