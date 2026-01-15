import base64
import json
from datetime import datetime
from typing import Any
from uuid import UUID

from luml.schemas.general import CursorType


class PaginationMixin:
    METRICS_SORT_KEY = "metrics"
    CREATED_AT_SORT_KEY = "created_at"

    @staticmethod
    def encode_cursor(cursor_id: UUID, cursor_value: CursorType, sort_by: str) -> str:
        if isinstance(cursor_value, datetime):
            cursor_value = cursor_value.isoformat()
        cursor_string = json.dumps([cursor_id.hex, cursor_value, sort_by])
        return base64.urlsafe_b64encode(cursor_string.encode()).decode()

    def decode_cursor(
        self,
        cursor_str: str | None,
    ) -> tuple[None, None, None, None] | tuple[UUID, CursorType, str, str | None]:
        if not cursor_str:
            return None, None, None, None
        try:
            cursor_id, cursor_value, sort_by = json.loads(
                base64.urlsafe_b64decode(cursor_str.encode()).decode()
            )

            metric_key = None
            metrics_prefix = f"{self.METRICS_SORT_KEY}:"
            if sort_by.startswith(metrics_prefix):
                _, metric_key = sort_by.split(":", 1)
                sort_by = self.METRICS_SORT_KEY

            if sort_by == self.CREATED_AT_SORT_KEY and isinstance(cursor_value, str):
                cursor_value = datetime.fromisoformat(cursor_value)

            return UUID(cursor_id), cursor_value, sort_by, metric_key
        except Exception:
            return None, None, None, None

    def get_cursor(
        self, items: list[Any], limit: int, sort_by: str, metric_key: str | None = None
    ) -> str | None:
        if not items:
            return None

        if len(items) > limit:
            cursor_rec = items[limit - 1]

            if sort_by == self.METRICS_SORT_KEY and metric_key:
                cursor_value = cursor_rec.metrics.get(metric_key)
                sort_by_encoded = f"{self.METRICS_SORT_KEY}:{metric_key}"
            else:
                cursor_value = getattr(cursor_rec, sort_by)
                sort_by_encoded = sort_by

            return self.encode_cursor(cursor_rec.id, cursor_value, sort_by_encoded)

        return None
