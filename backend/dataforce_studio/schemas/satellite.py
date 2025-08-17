from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from dataforce_studio.schemas.base import BaseOrmConfig


class SatelliteCapability(StrEnum):
    DEPLOY = "deploy"


class SatelliteTaskType(StrEnum):
    PAIRING = "pairing"
    DEPLOY = "deploy"


class SatelliteTaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class Satellite(BaseModel, BaseOrmConfig):
    id: int
    orbit_id: int
    name: str | None = None
    paired: bool
    capabilities: list[SatelliteCapability]
    created_at: datetime
    updated_at: datetime | None = None
    last_seen_at: datetime | None = None


class SatelliteCreateIn(BaseModel, BaseOrmConfig):
    name: str | None = None


class SatelliteCreate(BaseModel, BaseOrmConfig):
    orbit_id: int
    api_key_hash: str
    name: str | None = None


class SatellitePairIn(BaseModel):
    capabilities: list[SatelliteCapability]


class SatelliteQueueTask(BaseModel, BaseOrmConfig):
    id: int
    satellite_id: int
    orbit_id: int
    type: SatelliteTaskType
    payload: dict
    status: SatelliteTaskStatus
    scheduled_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    result: dict | None = None
    created_at: datetime
    updated_at: datetime | None = None


class SatelliteCreateOut(BaseModel, BaseOrmConfig):
    satellite: Satellite
    api_key: str
    task: SatelliteQueueTask


class SatelliteTaskUpdateIn(BaseModel):
    status: SatelliteTaskStatus
    result: dict | None = None
