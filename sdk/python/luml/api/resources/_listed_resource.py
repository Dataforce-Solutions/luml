from collections.abc import AsyncIterator, Iterator
from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedList(BaseModel, Generic[T]):
    items: list[T]
    cursor: str | None = None


class ListMethod(Protocol[T]):
    def __call__(
        self, *, start_after: str | None = None, limit: int | None = None, **kwargs
    ) -> PaginatedList[T]: ...


class ListedResource:
    @staticmethod
    def _auto_paginate(
        list_method: ListMethod[T], limit: int = 100, **params
    ) -> Iterator[T]:
        start_after = None
        while True:
            page = list_method(start_after=start_after, limit=limit, **params)

            yield from page.items

            if page.cursor is None:
                break

            start_after = page.cursor

    @staticmethod
    async def _auto_paginate_async(
        list_method: ListMethod[T], limit: int = 100, **params
    ) -> AsyncIterator[T]:
        start_after = None
        while True:
            page = await list_method(start_after=start_after, limit=limit, **params)

            for item in page.items:
                yield item

            if page.cursor is None:
                break

            start_after = page.cursor
