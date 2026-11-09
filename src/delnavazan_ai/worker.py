"""Background worker entrypoint.

Deliberately disabled until a durable queue, leases and retry semantics are implemented.
"""


def main() -> None:
    raise SystemExit("Worker not configured: queue implementation pending AI-01")


if __name__ == "__main__":
    main()
