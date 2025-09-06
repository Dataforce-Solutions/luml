from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class InferenceAccessIn(BaseModel):
    api_key: str


class InferenceAccessOut(BaseModel):
    authorized: bool


def create_agent_app(authorize_access: Callable[[str], Awaitable[bool]]) -> FastAPI:
    app = FastAPI()

    @app.post("/satellites/deployments/inference-access", response_model=InferenceAccessOut)
    async def authorize_inference_access(body: InferenceAccessIn) -> InferenceAccessOut:  # noqa: D401
        try:
            authorized = bool(await authorize_access(body.api_key))
            return InferenceAccessOut(authorized=authorized)
        except Exception as err:
            raise HTTPException(status_code=502, detail="Authorization check failed") from err

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    return app
