from datetime import datetime

from pydantic import BaseModel

from dataforce_studio.schemas.base import BaseOrmConfig
from dataforce_studio.schemas.user import UserOut


class APIKeyCreate(BaseModel):
    user_id: int
    hash: str


class APIKeyOut(BaseModel, BaseOrmConfig):
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None


class APIKeyCreateOut(APIKeyOut):
    key: str | None = None


class APIKeyAuthOut(APIKeyOut):
    user: UserOut
    created_at: datetime
    updated_at: datetime | None = None
