from enum import StrEnum
from typing import Any, Union

import shortuuid
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema
from uuid6 import UUID


class ShortUUIDMeta(type):
    def __instancecheck__(cls, instance: Any) -> bool:  # noqa: ANN401
        if type(instance) is cls:
            return True

        if isinstance(instance, str):
            return cls._is_valid_short_uuid(instance) or cls._is_valid_uuid(instance)

        return False

    @staticmethod
    def _is_valid_short_uuid(value: str | UUID) -> bool:
        try:
            if isinstance(value, UUID):
                value = str(value)
            if isinstance(value, str):
                shortuuid.decode(value)
                return True
            return False
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _is_valid_uuid(value: str | UUID) -> bool:
        try:
            if isinstance(value, UUID):
                return True
            if isinstance(value, str):
                UUID(value)
                return True
            return False
        except (ValueError, TypeError):
            return False


class ShortUUID(metaclass=ShortUUIDMeta):
    __slots__ = ("_value",)

    def __init__(self, value: Union[str, UUID, "ShortUUID"]) -> None:
        if type(value) is ShortUUID:
            self._value = value._value
        elif isinstance(value, str | UUID):
            self._value = self._validate_short_uuid(value)
        else:
            raise TypeError(
                f"ShortUUID expects str, UUID, or ShortUUID, got {type(value).__name__}"
            )

    def __str__(self) -> str:
        return self.to_short()

    def __repr__(self) -> str:
        return f"ShortUUID('{self._value}')"

    def __eq__(self, other: Any) -> bool:  # noqa: ANN401
        if type(other) is ShortUUID:
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False

    def __hash__(self) -> int:
        return hash(self._value)

    @property
    def value(self) -> str:
        return self._value

    def to_short(self) -> str:
        return self._uuid_to_short(self._value)

    def to_uuid(self) -> str:
        return self._short_to_uuid(self._value)

    @staticmethod
    def _uuid_to_short(full_uuid: Union[str, UUID, "ShortUUID"]) -> str:
        if isinstance(full_uuid, UUID):
            full_uuid = str(full_uuid)
        return shortuuid.encode(UUID(full_uuid))

    @staticmethod
    def _short_to_uuid(short_uuid: Union[str, UUID, "ShortUUID"]) -> str:
        if isinstance(short_uuid, UUID):
            return str(short_uuid)
        if ShortUUID._is_valid_uuid(short_uuid):
            return short_uuid
        return str(shortuuid.decode(short_uuid))

    @staticmethod
    def _is_valid_short_uuid(value: Union[str, UUID, "ShortUUID"]) -> bool:
        try:
            if isinstance(value, UUID):
                value = str(value)
            if isinstance(value, str):
                shortuuid.decode(value)
                return True
            return False
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _is_valid_uuid(value: Union[str, UUID, "ShortUUID"]) -> bool:
        try:
            if isinstance(value, UUID):
                return True
            if isinstance(value, str):
                UUID(value)
                return True
            return False
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _validate_short_uuid(value: Union[str, UUID, "ShortUUID"]) -> str:
        if hasattr(value, "__str__") and not isinstance(value, str):
            value = str(value)

        if isinstance(value, str):
            if ShortUUID._is_valid_short_uuid(value):
                return str(ShortUUID._short_to_uuid(value))
            if ShortUUID._is_valid_uuid(value):
                return value
            raise ValueError(f"Invalid UUID format: {value}")

        raise ValueError(f"Invalid UUID format: {value}")

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> core_schema.CoreSchema:
        def validate(value: str | UUID | ShortUUID) -> ShortUUID:
            return cls(value)

        def serialize(value: ShortUUID) -> str:
            return value.to_short()

        return core_schema.with_info_plain_validator_function(
            lambda v, _: validate(v),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize,
                return_schema=core_schema.str_schema(),
                when_used="json",
            ),
        )


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
