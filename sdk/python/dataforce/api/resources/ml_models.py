import builtins
from typing import TYPE_CHECKING

from .._types import MLModel

if TYPE_CHECKING:
    from .._client import AsyncDataForceClient, DataForceClient



class MLModelResource:
    def __init__(self, client: "DataForceClient") -> None:
        self._client = client

    def list(
        self, organization_id: int, orbit_id: int, collection_id: int
    ) -> list[MLModel]:
        response = self._client.get(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models"
        )
        if response is None:
            return []
        return [MLModel.model_validate(model) for model in response]

    def download_url(
        self, organization_id: int, orbit_id: int, collection_id: int, model_id: int
    ) -> dict:
        return self._client.get(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models/{model_id}/download-url"
        )

    def delete_url(
        self, organization_id: int, orbit_id: int, collection_id: int, model_id: int
    ) -> dict:
        return self._client.get(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models/{model_id}/delete-url"
        )

    def create(
        self,
        organization_id: int,
        orbit_id: int,
        collection_id: int,
        file_name: str,
        metrics: dict,
        manifest: dict,
        file_hash: str,
        file_index: dict[str, tuple[int, int]],
        size: int,
        model_name: str | None = None,
        description: str | None = None,
        tags: builtins.list[str] | None = None,
    ) -> MLModel:
        return self._client.post(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models",
            json={
                "file_name": file_name,
                "metrics": metrics,
                "manifest": manifest,
                "file_hash": file_hash,
                "file_index": file_index,
                "size": size,
                "model_name": model_name,
                "description": description,
                "tags": tags,
            },
        )

    def update(
        self,
        organization_id: int,
        orbit_id: int,
        collection_id: int,
        model_id: int,
        file_name: str | None = None,
        model_name: str | None = None,
        description: str | None = None,
        tags: builtins.list[str] | None = None,
        status: str | None = None,
    ) -> MLModel:
        return self._client.patch(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models/{model_id}",
            json=self._client.filter_none(
                {
                    "file_name": file_name,
                    "model_name": model_name,
                    "description": description,
                    "tags": tags,
                    "status": status,
                }
            ),
        )

    def delete(
        self, organization_id: int, orbit_id: int, collection_id: int, model_id: int
    ) -> None:
        return self._client.delete(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models/{model_id}"
        )


class AsyncMLModelResource:
    def __init__(self, client: "AsyncDataForceClient") -> None:
        self._client = client

    async def list(
        self, organization_id: int, orbit_id: int, collection_id: int
    ) -> list[MLModel]:
        response = await self._client.get(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models"
        )
        if response is None:
            return []
        return [MLModel.model_validate(model) for model in response]

    async def download_url(
        self, organization_id: int, orbit_id: int, collection_id: int, model_id: int
    ) -> dict:
        return await self._client.get(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models/{model_id}/download-url"
        )

    async def delete_url(
        self, organization_id: int, orbit_id: int, collection_id: int, model_id: int
    ) -> dict:
        return await self._client.get(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models/{model_id}/delete-url"
        )

    async def create(
        self,
        organization_id: int,
        orbit_id: int,
        collection_id: int,
        file_name: str,
        metrics: dict,
        manifest: dict,
        file_hash: str,
        file_index: dict[str, tuple[int, int]],
        size: int,
        model_name: str | None = None,
        description: str | None = None,
        tags: builtins.list[str] | None = None,
    ) -> MLModel:
        return await self._client.post(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models",
            json={
                "file_name": file_name,
                "metrics": metrics,
                "manifest": manifest,
                "file_hash": file_hash,
                "file_index": file_index,
                "size": size,
                "model_name": model_name,
                "description": description,
                "tags": tags,
            },
        )

    async def update(
        self,
        organization_id: int,
        orbit_id: int,
        collection_id: int,
        model_id: int,
        file_name: str | None = None,
        model_name: str | None = None,
        description: str | None = None,
        tags: builtins.list[str] | None = None,
        status: str | None = None,
    ) -> MLModel:
        return await self._client.patch(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models/{model_id}",
            json=self._client.filter_none(
                {
                    "file_name": file_name,
                    "model_name": model_name,
                    "description": description,
                    "tags": tags,
                    "status": status,
                }
            ),
        )

    async def delete(
        self, organization_id: int, orbit_id: int, collection_id: int, model_id: int
    ) -> None:
        return await self._client.delete(
            f"/organizations/{organization_id}/orbits/{orbit_id}/collections/{collection_id}/ml-models/{model_id}"
        )
