from fastapi import FastAPI, Response, status

from .database import is_ready

app = FastAPI(title="Delnavazan AI", version="0.1.0")


@app.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready")
def readiness(response: Response) -> dict[str, str]:
    if not is_ready():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready"}
    return {"status": "ready"}
