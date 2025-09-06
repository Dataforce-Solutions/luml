import os
import json
import random
import time

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, status

app = FastAPI()

AGENT_URL = os.getenv("SATELLITE_AGENT_URL", "http://host.docker.internal:7000").rstrip("/")


@app.get("/healthz")
def healthz() -> dict:
    return dict(
        status="ok",
    )


def require_api_key(request: Request) -> None:
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")
    api_key = auth.split()[1]

    try:
        r = httpx.post(
            f"{AGENT_URL}/satellites/deployments/inference-access",
            json={"api_key": api_key},
            timeout=5.0,
        )
        r.raise_for_status()
        data = r.json()
        if not bool(data.get("authorized")):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Authorization check failed"
        )


@app.get("/")
def root(_: None = Depends(require_api_key)):
    return {
        "random": random.random(),
        "ts": time.time(),
        "model_artifact_url": os.getenv("MODEL_ARTIFACT_URL", ""),
        "secrets": json.loads(os.getenv("MODEL_SECRETS", "{}")),
    }
