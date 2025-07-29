from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._client import AsyncDataForceClient, DataForceClient


class APIResource(ABC):
    @abstractmethod
    def _get(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        raise NotImplementedError()

    @abstractmethod
    def _post(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        raise NotImplementedError()

    @abstractmethod
    def _put(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        raise NotImplementedError()

    @abstractmethod
    def _patch(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        raise NotImplementedError()

    @abstractmethod
    def _delete(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        raise NotImplementedError()

    def _filter_none(self, data: dict[str, Any]) -> dict[str, Any]:  # noqa: ANN401
        return {key: value for key, value in data.items() if value is not None}


class AsyncAPIResource(APIResource):
    _client: AsyncDataForceClient

    def __init__(self, client: AsyncDataForceClient) -> None:
        self._client = client

    async def _get(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        return await self._client.request("GET", url, **kwargs)

    async def _post(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        return await self._client.request("POST", url, **kwargs)

    async def _put(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        return await self._client.request("PUT", url, **kwargs)

    async def _patch(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        return await self._client.request("PATCH", url, **kwargs)

    async def _delete(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        return await self._client.request("DELETE", url, **kwargs)


class SyncAPIResource(APIResource):
    _client: DataForceClient

    def __init__(self, client: DataForceClient) -> None:
        self._client = client

    def _get(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        return self._client.request("GET", url, **kwargs)

    def _post(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        return self._client.request("POST", url, **kwargs)

    def _put(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        return self._client.request("PUT", url, **kwargs)

    def _patch(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        return self._client.request("PATCH", url, **kwargs)

    def _delete(self, url: str, **kwargs) -> Any:  # noqa: ANN401
        return self._client.request("DELETE", url, **kwargs)
