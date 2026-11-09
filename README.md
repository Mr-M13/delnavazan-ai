# Delnavazan AI (AI-01 scaffold)

Private, isolated customer-support service. **Not production ready.** No customer messages, AI responses or external provider calls are enabled.

## Local setup
```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
uvicorn delnavazan_ai.app:app --reload
```

- `GET /health/live`: process liveness.
- `GET /health/ready`: configuration-only readiness placeholder; **not** a real database connectivity probe yet.
- `migrations/001_initial.sql`: initial schema, not yet managed by a migration runner.
- `worker.py`: intentionally disabled until durable queue implementation.

## Safety
Use dedicated PostgreSQL, never WordPress database credentials. Do not set live Meta/Chatwoot/OpenAI tokens before integration review. All outbound communication is disabled by default. No deploy without explicit approval.

## Remaining AI-01 work
Implement real DB connectivity/readiness, migration runner and rollback, durable leased worker, retry/dead-letter handling, redacted structured logs, correlation IDs, integration tests and secret scanning. Validate on supported hosting before any launch.

## AI-02 draft: public Persian conversation engine
- `conversation.py` enforces public-only approved reference excerpts and conservative escalation.
- `openai_adapter.py` uses OpenAI Responses API with `store=False`; no API calls happen in offline tests.
- No public knowledge ingestion, fact verification, webhook, user-facing route or messaging transport is connected yet.
- The AI flag defaults to false. Do not enable in production without security and knowledge-source review.
