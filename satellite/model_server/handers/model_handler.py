from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
import tempfile
from fnnx.handlers._common import unpack_model
from pydantic import Field, create_model
import json
import os
from fnnx.device import DeviceMap
from fnnx.handlers.local import LocalHandler, LocalHandlerConfig

from .file_handler import FileHandler

try:
    import numpy as _np  # optional

    _HAS_NUMPY = True
except Exception:
    _HAS_NUMPY = False


class ModelHandler:
    def __init__(self, url: str | None = None):
        self._model_url = os.getenv("MODEL_ARTIFACT_URL", "") if url is None else url
        self._file_handler = FileHandler()
        self._cached_models = {}  # url -> local_path mapping
        self.model_path = self.get_model_path()

    def _download_model(self, url: str) -> str:
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name or "model.dfs"

        temp_dir = tempfile.mkdtemp(prefix="dfs_model_")
        local_path = Path(temp_dir) / filename

        return self._file_handler.download_file(url, str(local_path))

    def get_model_path(self) -> str:
        if not self._model_url.startswith(("http://", "https://")):
            return self._model_url

        if self._model_url in self._cached_models:
            cached_path = self._cached_models[self._model_url]
            if Path(cached_path).exists():
                return cached_path

        local_path = self._download_model(self._model_url)

        self._cached_models[self._model_url] = local_path

        return local_path

    @staticmethod
    def get_base_type(dtype_inner: str):
        return {
            "string": str,
            "integer": int,
            "float": float,
            "float32": float,
            "float64": float,
            "int": int,
            "int32": int,
            "int64": int,
            "boolean": bool,
        }.get(dtype_inner, Any)

    def to_jsonable(self, obj):
        if _HAS_NUMPY:
            if isinstance(obj, _np.ndarray):
                return obj.tolist()
            if isinstance(obj, _np.generic):
                return obj.item()
        if isinstance(obj, dict):
            return {k: self.to_jsonable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.to_jsonable(v) for v in obj]
        if isinstance(obj, tuple):
            return [self.to_jsonable(v) for v in obj]
        return obj

    @staticmethod
    def create_nested_list_type(base_type, shape):
        for _ in range(len(shape)):
            base_type = List[base_type]
        return base_type

    def get_field_type(
        self, content_type: str, dtype: str, shape: Optional[List[Union[int, str]]] = None
    ):
        if content_type == "NDJSON":
            if dtype.startswith("Array["):
                inner = dtype[6:-1]
                base_type = self.get_base_type(inner)
            elif dtype.startswith("NDContainer["):
                inner = dtype[12:-1]
                base_type = Dict[str, Any]
            else:
                raise ValueError(f"Unsupported dtype for NDJSON: {dtype}")

            if shape:
                return self.create_nested_list_type(base_type, shape)
            else:
                return List[base_type]

        elif content_type == "JSON":
            return Dict[str, Any]

        return Any

    def create_input_model(self, manifest: dict):
        fields = {}

        for input_spec in manifest["inputs"]:
            name = input_spec["name"]
            dtype = input_spec["dtype"]
            content_type = input_spec["content_type"]
            field_type = self.get_field_type(
                content_type, dtype, shape=input_spec.get("shape", None)
            )

            description = input_spec.get("description", f"Input field of type {dtype}")

            fields[name] = (field_type, Field(..., description=description))
        return create_model("InputsModel", **fields)

    @staticmethod
    def create_dynamic_attributes_model(manifest: dict):
        fields = {}
        for attr in manifest.get("dynamic_attributes", []):
            name = attr["name"]
            desc = attr.get("description", f"Dynamic attribute '{name}'")
            fields[name] = (Optional[str], Field(default=f"<<<{name}>>>", description=desc))
        return create_model("DynamicAttributesModel", **fields)

    def unpacked_model_path(self):
        extracted_path, *_ = unpack_model(self.model_path)
        return extracted_path

    def get_manifest(self):
        manifest_path = Path(self.unpacked_model_path()) / "manifest.json"
        with open(manifest_path) as f:
            return json.load(f)

    def load_dtypes_schemas(self) -> dict[str, Any]:
        dtypes_path = Path(self.unpacked_model_path()) / "dtypes.json"
        if dtypes_path.exists():
            with open(dtypes_path) as f:
                return json.load(f)
        return {}

    async def compute_result(self, inputs, dynamic_attributes):
        extracted_path = self.unpacked_model_path()

        device_map = DeviceMap(accelerator="cpu", node_device_map={})
        handler = LocalHandler(
            model_path=extracted_path,
            device_map=device_map,
            handler_config=LocalHandlerConfig(auto_cleanup=False),
        )

        result = await handler.compute_async(inputs, dynamic_attributes)
        return self.to_jsonable(result)
