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

## AI-01 database and job foundation (development branch)
- `python -m delnavazan_ai.migrate` applies forward-only numbered SQL migrations to a **dedicated** database. Rollback migrations are not implemented.
- `/health/ready` now checks actual PostgreSQL connectivity.
- `python -m delnavazan_ai.worker` polls a durable leased job queue; **no handlers are registered**, so it cannot send messages.
- Job retries use exponential backoff and dead-letter after maximum attempts.
- Database integration tests and production-grade shutdown/monitoring remain pending.
