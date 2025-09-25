import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from agent.handlers.handler_instances import ms_handler, secrets_handler
from agent.schemas.deployments import (
    DeploymentInfo,
    Healthz,
    InferenceAccessIn,
    InferenceAccessOut,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    asyncio.create_task(ms_handler.sync_deployments())
    asyncio.create_task(secrets_handler.initialize())

    yield

    # await model_server_handler.shutdown()


def create_agent_app(authorize_access: Callable[[str], Awaitable[bool]]) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    security = HTTPBearer()

    async def verify_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
    ) -> bool:
        try:
            authorized = await authorize_access(credentials.credentials)
            if not authorized:
                raise HTTPException(status_code=401, detail="Invalid API key")
            return True
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(status_code=502, detail="Authorization failed") from error

    @app.post("/satellites/deployments/inference-access", response_model=InferenceAccessOut)
    async def authorize_inference_access(body: InferenceAccessIn) -> InferenceAccessOut:  # noqa: D401
        try:
            authorized = bool(await authorize_access(body.api_key))
            return InferenceAccessOut(authorized=authorized)
        except Exception as err:
            raise HTTPException(
                status_code=502, detail=f"Authorization check failed: {str(err)}"
            ) from err

    @app.get("/healthz", response_model=Healthz)
    def healthz() -> dict:
        return {"status": "healthy"}

    @app.get("/deployments", response_model=list[DeploymentInfo])
    async def deployments(authorized: bool = Depends(verify_token)) -> list[dict]:  # noqa: B008
        local_deployments = await ms_handler.list_active_deployments()
        return [{"deployment_id": deployment.deployment_id} for deployment in local_deployments]

    @app.post("/deployments/{deployment_id}/compute", response_model=dict)
    async def compute(
        deployment_id: int, body: dict, authorized: bool = Depends(verify_token)  # noqa: B008
    ) -> dict:
        try:
            return await ms_handler.model_compute(deployment_id, body)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Compute failed: {str(e)}") from e

    return app
