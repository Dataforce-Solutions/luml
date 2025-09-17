from typing import Any
from pydantic import ValidationError, create_model, Field

from handers.model_handler import ModelHandler
from service import UvicornService
from auth import HTTPException

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
async def get_manifest():
    try:
        return model_handler.get_manifest()
    except Exception as e:
        return {"error": f"Failed to get manifest: {str(e)}"}


@app.post(
    "/compute",
    summary="Run Model Inference",
    description="Execute inference on the loaded model",
    response_model=dict[str, Any],
    tags=["model"],
)
async def compute(request_data):
    try:
        manifest = model_handler.get_manifest()
        input_model = model_handler.create_input_model(manifest)
        dynamic_attrs_model = model_handler.create_dynamic_attributes_model(manifest)

        ComputeRequest = create_model(
            "ComputeRequest",
            inputs=(input_model, Field(..., description="Input data for the model")),
            dynamic_attributes=(
                dynamic_attrs_model,
                Field(default_factory=dict, description="Dynamic attributes"),
            ),
        )

        # Валидация запроса
        try:
            validated_request = ComputeRequest(**request_data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=f"Input validation failed: {e}")

        print(f"Validated inputs: {validated_request.inputs}")
        print(f"Validated dynamic_attributes: {validated_request.dynamic_attributes}")

        # Выполнение вычислений
        try:
            result = await model_handler.compute_result(
                validated_request.inputs, validated_request.dynamic_attributes
            )
            print(f"Compute result: {result}")
            return result
        except Exception as e:
            print(f"Model computation error: {e}")
            raise HTTPException(status_code=500, detail=f"Model computation failed: {e}")

    except HTTPException:
        # Перебрасываем HTTPException дальше, не обрабатываем здесь
        raise
    except Exception as e:
        return {"error": f"Server error: {str(e)}"}
