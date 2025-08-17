from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from dataforce_studio.schemas.base import BaseOrmConfig


class DeploymentStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    FAILED = "failed"
    DELETED = "deleted"


class Deployment(BaseModel, BaseOrmConfig):
    id: int
    orbit_id: int
    satellite_id: int
    model_uri: str
    inference_url: str | None = None
    status: DeploymentStatus
    secret_ids: list[int] = Field(default_factory=list)
    created_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None


class DeploymentCreate(BaseModel, BaseOrmConfig):
    orbit_id: int
    satellite_id: int
    model_uri: str
    secret_ids: list[int] = Field(default_factory=list)
    status: DeploymentStatus = DeploymentStatus.PENDING
    created_by_user_id: int | None = None


class DeploymentCreateIn(BaseModel):
    satellite_id: int
    model_artifact_id: int
    secret_ids: list[int] = Field(default_factory=list)


class DeploymentUpdate(BaseModel, BaseOrmConfig):
    id: int
    inference_url: str | None = None
    status: DeploymentStatus | None = None


class DeploymentUpdateIn(BaseModel):
    inference_url: str
