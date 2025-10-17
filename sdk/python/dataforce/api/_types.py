from enum import StrEnum

from uuid6 import UUID

try:
    from pydantic import BaseModel

    HAS_PYDANTIC = True
except (ImportError, ModuleNotFoundError):
    HAS_PYDANTIC = False
    from typing import Any, get_args, get_origin

    class BaseModel:
        def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401
            annotations = getattr(self.__class__, "__annotations__", {})

            for field_name, field_type in annotations.items():
                if field_name in kwargs:
                    validated_value = self._validate_type(
                        field_name, kwargs[field_name], field_type
                    )
                    setattr(self, field_name, validated_value)
                else:
                    if not self._has_default_value(
                        field_name
                    ) and not self._is_optional_type(field_type):
                        raise ValueError(f"Missing required field: {field_name}")
                    if self._has_default_value(field_name):
                        setattr(self, field_name, getattr(self.__class__, field_name))

            for key, value in kwargs.items():
                if key not in annotations:
                    setattr(self, key, value)

        @classmethod
        def _has_default_value(cls, field_name: str) -> bool:
            return hasattr(cls, field_name) and field_name in cls.__dict__

        @classmethod
        def _is_optional_type(cls, field_type: Any) -> bool:  # noqa: ANN401
            return get_origin(field_type) is not None and type(None) in get_args(
                field_type
            )

        @classmethod
        def _get_base_type(cls, field_type: Any) -> Any:  # noqa: ANN401
            origin = get_origin(field_type)
            if origin is not None:
                args = get_args(field_type)
                non_none_types = [arg for arg in args if arg is not type(None)]
                if len(non_none_types) < len(args):
                    if non_none_types:
                        inner_type = non_none_types[0]
                        inner_origin = get_origin(inner_type)
                        if inner_origin is not None:
                            return inner_origin
                        return inner_type
                else:
                    return origin
            return field_type

        @classmethod
        def _validate_type(cls, field_name: str, value: Any, field_type: Any) -> Any:  # noqa: ANN401
            if value is None:
                if cls._is_optional_type(field_type):
                    return None
                raise ValueError(f"Field '{field_name}' ids required")

            expected_type = cls._get_base_type(field_type)

            if type(value) is not expected_type:
                raise ValueError(f"Invalid value type for '{field_name}' field")
            return value

        @classmethod
        def model_validate(cls, data: dict[str, Any]) -> "BaseModel":  # noqa: ANN401
            return cls(**data)

        def model_dump(self) -> dict[str, Any]:  # noqa: ANN401
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

        def __str__(self) -> str:
            return " ".join([f"{k}={v}" for k, v in self.__dict__.items()])

        def __repr__(self) -> str:
            return f"{self.__class__.__name__}({self.__str__()})"


def is_uuid(value: str | None) -> bool:
    if value is None:
        return False
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


class Organization(BaseModel):
    id: str
    name: str
    logo: str | None = None
    created_at: str
    updated_at: str | None = None


class BucketSecret(BaseModel):
    id: str
    endpoint: str
    bucket_name: str
    secure: bool | None = None
    region: str | None = None
    cert_check: bool | None = None
    organization_id: str
    created_at: str
    updated_at: str | None = None


class Orbit(BaseModel):
    id: str
    name: str
    organization_id: str
    bucket_secret_id: str
    total_members: int | None = None
    total_collections: int | None = None
    created_at: str
    updated_at: str | None = None


class CollectionType(StrEnum):
    MODEL = "model"
    DATASET = "dataset"


class ModelArtifactStatus(StrEnum):
    PENDING_UPLOAD = "pending_upload"
    UPLOADED = "uploaded"
    UPLOAD_FAILED = "upload_failed"
    DELETION_FAILED = "deletion_failed"


class Collection(BaseModel):
    id: str
    orbit_id: str
    description: str
    name: str
    collection_type: str
    tags: list[str] | None = None
    total_models: int
    created_at: str
    updated_at: str | None = None


class ModelArtifact(BaseModel):
    id: str
    collection_id: str
    file_name: str
    model_name: str | None = None
    description: str | None = None
    metrics: dict
    manifest: dict
    file_hash: str
    file_index: dict[str, tuple[int, int]]
    bucket_location: str
    size: int
    unique_identifier: str
    tags: list[str] | None = None
    status: str
    created_at: str
    updated_at: str | None = None


class ModelDetails(BaseModel):
    file_name: str
    metrics: dict
    manifest: dict
    file_hash: str
    file_index: dict[str, tuple[int, int]]
    size: int
