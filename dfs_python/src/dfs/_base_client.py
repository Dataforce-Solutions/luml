from abc import ABC, abstractmethod
from typing import Any

import httpx
from httpx import URL


class BaseClient(ABC):
    def __init__(
        self,
        base_url: str | URL,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url
        self._timeout = timeout

    @property
    def base_url(self) -> URL:
        return self._base_url

    @base_url.setter
    def base_url(self, url: URL) -> None:
        self._base_url = url

    @property
    def timeout(self) -> float:
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        self._timeout = timeout

    @property
    def auth_headers(self) -> dict[str, str]:
        return {}

    @property
    def default_headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "dataforce-sdk/0.1.0",
            **self.auth_headers,
        }

    @abstractmethod
    def _process_response(self, response: httpx.Response) -> dict | None:
        raise NotImplementedError()

    @abstractmethod
    def request(
        self,
        method: str,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        raise NotImplementedError()


class SyncBaseClient(BaseClient):
    _client: httpx.Client

    def __init__(
        self,
        base_url: str | URL,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(base_url=base_url, timeout=timeout)
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def _process_response(self, response: httpx.Response) -> dict | None:
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def request(
        self,
        method: str,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        final_headers = {**self.default_headers}
        if headers:
            final_headers.update(headers)

        response = self._client.request(
            method=method,
            url=url,
            headers=final_headers,
            json=json,
            params=params,
            **kwargs,
        )
        return self._process_response(response)


class AsyncBaseClient(BaseClient):
    _client: httpx.AsyncClient

    def __init__(
        self,
        base_url: str | URL,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(base_url=base_url, timeout=timeout)
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def _process_response(self, response: httpx.Response) -> dict | None:
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    async def request(
        self,
        method: str,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        final_headers = {**self.default_headers}
        if headers:
            final_headers.update(headers)

        response = await self._client.request(
            method=method,
            url=url,
            headers=final_headers,
            json=json,
            params=params,
            **kwargs,
        )
        return await self._process_response(response)
