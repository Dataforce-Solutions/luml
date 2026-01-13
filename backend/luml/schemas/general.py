from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


type CursorType = int | str | float | datetime


class PaginationParams(BaseModel):
    cursor_id: UUID | None = None
    cursor_value: Any | None = None
    sort_by: str | None = None
    order: SortOrder = SortOrder.DESC
    limit: int = 100
    metric_key: str | None = None
