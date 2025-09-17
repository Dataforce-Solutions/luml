from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.handlers.model_server_handler import ModelServerHandler


class InferenceAccessIn(BaseModel):
    api_key: str


class InferenceAccessOut(BaseModel):
    authorized: bool


model_server_handler = ModelServerHandler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await model_server_handler.sync_deployments()

    yield

    # await model_server_handler.shutdown()


def create_agent_app(authorize_access: Callable[[str], Awaitable[bool]]) -> FastAPI:
    app = FastAPI(lifespan=lifespan)

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

    @app.get("/deployments")
    async def deployments():
        return await model_server_handler.list_active_deployments()

    @app.post("/deployments/{deployment_id}/compute")
    async def compute(deployment_id: int, body: dict):
        try:
            return await model_server_handler.model_compute(deployment_id, body)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Compute failed: {str(e)}")

    @app.get("/deployments/{deployment_id}/manifest")
    async def manifest(deployment_id: int):
        try:
            return await model_server_handler.model_manifest(deployment_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Manifest retrieval failed: {str(e)}")

    return app
