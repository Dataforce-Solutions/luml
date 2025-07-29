from typing import TYPE_CHECKING

from .._types import Organization

if TYPE_CHECKING:
    from .._client import AsyncDataForceClient, DataForceClient


class OrganizationResource:
    def __init__(self, client: "DataForceClient") -> None:
        self._client = client

    def list(self) -> list[Organization]:
        response = self._client.get("/users/me/organizations")
        if response is None:
            return []
        return [Organization.model_validate(org) for org in response]


class AsyncOrganizationResource:
    def __init__(self, client: "AsyncDataForceClient") -> None:
        self._client = client

    async def list(self) -> list[Organization]:
        response = await self._client.get("/users/me/organizations")
        if response is None:
            return []
        return [Organization.model_validate(org) for org in response]

    # async def create(self, name: str, logo: str | None = None) -> Organization:
    #     response = await self._post(
    #         "/organizations",
    #         json={"name": name, "logo": logo}
    #     )
    #     return Organization(**response)
    #
    # async def update(
    #     self, organization_id: int, name: str | None = None, logo: str | None = None
    # ) -> Organization:
    #     response = await self._patch(
    #         f"/organizations/{organization_id}",
    #         json={"id": organization_id, "name": name, "logo": logo},
    #     )
    #     return Organization(**response)
