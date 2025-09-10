from typing import Any

from auth import require_api_key
from handers.model_handler import ModelHandler
from service import UvicornService

app = UvicornService()
model_handler = ModelHandler()


@app.get(
    "/healthz",
    summary="Health Check",
    description="Returns the health status of the service",
    tags=["model"],
)
async def healthz():
    return {"status": "healthy"}


@app.get(
    "/manifest",
    summary="Get Model Manifest",
    description="Returns the FNNX model manifest with input/output specifications",
    tags=["model"],
)
async def get_manifest(scope):
    require_api_key(scope)
    return model_handler.get_manifest()


@app.post(
    "/compute",
    summary="Run Model Inference",
    description="Execute inference on the loaded model",
    response_model=dict[str, Any],
    tags=["model"],
)
async def compute(scope, request_data):
    require_api_key(scope)
    inputs = request_data.get("inputs", {})
    dynamic_attributes = request_data.get("dynamic_attributes", {}) or {}

    return await model_handler.compute_result(inputs, dynamic_attributes)
