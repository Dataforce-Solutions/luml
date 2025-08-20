from abc import ABC, abstractmethod
from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any

from .._types import Organization
from .._utils import find_by_value
from ._validators import validate_organization

if TYPE_CHECKING:
    from .._client import AsyncDataForceClient, DataForceClient


class OrganizationResourceBase(ABC):
    """Abstract Resource for managing Organizations."""

    @abstractmethod
    def get(
        self, organization_value: str | int | None = None
    ) -> Organization | None | Coroutine[Any, Any, Organization | None]:
        """Abstract method for selecting Organization details"""
        raise NotImplementedError()

    @abstractmethod
    def list(self) -> list[Organization] | Coroutine[Any, Any, list[Organization]]:
        """Abstract method for list all organizations available for user."""
        raise NotImplementedError()

    @abstractmethod
    def _get_by_name(
        self, name: str
    ) -> Organization | None | Coroutine[Any, Any, Organization | None]:
        """Abstract Method for search organization by name"""
        raise NotImplementedError()


class OrganizationResource(OrganizationResourceBase):
    """Resource for managing organizations."""

    def __init__(self, client: "DataForceClient") -> None:
        self._client = client

    @validate_organization
    def get(self, organization_value: str | int | None = None) -> Organization | None:
        """
        Get organization by name or ID.

        Retrieves organization details by its name or ID.
        Search by name is case-sensitive and matches exact organization names.

        Args:
            organization_value: The exact name or ID of the organization to retrieve.

        Returns:
            Organization object if found, None if organization
                with the specified name or ID is not found.

        Raises:
            MultipleResourcesFoundError: if there are several Organizations
                with that name.

        Example:
            >>> dfs = DataForceClient(api_key="dfs_your_key")
            >>> org_by_name = dfs.organizations.get("my-company")
            >>> org_by_id = dfs.organizations.get(123)

        Example response:
            >>> Organization(
            ...    id=123,
            ...    name="My Personal Company",
            ...    logo='https://example.com/',
            ...    created_at='2025-05-21T19:35:17.340408Z',
            ...    updated_at=None
            ...)
        """
        if isinstance(organization_value, str):
            return self._get_by_name(organization_value)
        if isinstance(organization_value, int):
            return self._get_by_id(organization_value)
        return None

    def list(self) -> list[Organization]:
        """
        List all organizations.

        Retrieves all organizations available for user.

        Returns:
            List of Organization objects.

        Example:
            >>> dfs = DataForceClient(api_key="dfs_your_key")
            >>> orgs = dfs.organizations.list()

        Example response:
            >>> [
            ...     Organization(
            ...         id=123,
            ...         name="My Personal Company",
            ...         logo='https://example.com/',
            ...         created_at='2025-05-21T19:35:17.340408Z',
            ...         updated_at=None
            ...     )
            ...]

        """
        response = self._client.get("/users/me/organizations")
        if response is None:
            return []
        return [Organization.model_validate(org) for org in response]

    def _get_by_name(self, name: str) -> Organization | None:
        """Private Method for search organization by name"""
        return find_by_value(self.list(), name)

    def _get_by_id(self, organization_id: int) -> Organization | None:
        """Private Method for retrieving Organization by id."""
        return find_by_value(
            self.list(), organization_id, lambda c: c.id == organization_id
        )


class AsyncOrganizationResource(OrganizationResourceBase):
    """Resource for managing organizations for async client."""

    def __init__(self, client: "AsyncDataForceClient") -> None:
        self._client = client

    @validate_organization
    async def get(
        self, organization_value: str | int | None = None
    ) -> Organization | None:
        """
        Get organization by name or ID.

        Retrieves organization details by its name or ID.
        Search by name is case-sensitive and matches exact organization names.

        Args:
            organization_value: The exact name or ID of the organization to retrieve.

        Returns:
            Organization object if found, None if organization
                with the specified name or ID is not found.

        Raises:
            MultipleResourcesFoundError: if there are several Organizations
                with that name.

        Example:
            >>> dfs = AsyncDataForceClient(api_key="dfs_your_key")
            >>> async def main():
            ...     org_by_name = await dfs.organizations.get("my-company")
            ...     org_by_id = await dfs.organizations.get(123)

        Example response:
            >>> Organization(
            ...    id=123,
            ...    name="My Personal Company",
            ...    logo='https://example.com/',
            ...    created_at='2025-05-21T19:35:17.340408Z',
            ...    updated_at=None
            ...)
        """
        if isinstance(organization_value, str):
            return await self._get_by_name(organization_value)
        if isinstance(organization_value, int):
            await self._get_by_id(organization_value)
        return None

    async def list(self) -> list[Organization]:
        """
        List all organizations.

        Retrieves all organizations available for user.

        Returns:
            List of Organization objects.

        Example:
            >>> dfs = AsyncDataForceClient(api_key="dfs_your_key")
            >>> async def main():
            ...     orgs = await dfs.organizations.list()

        Example response:
            >>> [
            ...     Organization(
            ...         id=123,
            ...         name="My Personal Company",
            ...         logo='https://example.com/',
            ...         created_at='2025-05-21T19:35:17.340408Z',
            ...         updated_at=None
            ...     )
            ...]
        """
        response = await self._client.get("/users/me/organizations")
        if response is None:
            return []
        return [Organization.model_validate(org) for org in response]

    async def _get_by_name(self, name: str) -> Organization | None:
        """Private Method for search organization by name"""
        return find_by_value(await self.list(), name)

    async def _get_by_id(self, organization_id: int) -> Organization | None:
        """Private Method for retrieving Organization by id."""
        return find_by_value(
            await self.list(), organization_id, lambda c: c.id == organization_id
        )

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
