import os
from abc import ABC, abstractmethod

import httpx

from ._base_client import AsyncBaseClient, SyncBaseClient
from ._exceptions import (
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    DataForceAPIError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    UnprocessableEntityError,
)
from .resources.bucket_secrets import AsyncBucketSecretResource, BucketSecretResource
from .resources.collections import AsyncCollectionResource, CollectionResource
from .resources.ml_models import AsyncMLModelResource, MLModelResource
from .resources.orbits import AsyncOrbitResource, OrbitResource
from .resources.organizations import AsyncOrganizationResource, OrganizationResource


class DataForceClientBase(ABC):
    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        if api_key is None:
            api_key = os.environ.get("DFS_API_KEY")
        if api_key is None:
            raise DataForceAPIError(
                "The api_key client option must be set either by "
                "passing api_key to the client or "
                "by setting the DFS_API_KEY environment variable"
            )
        self._api_key = api_key

        if base_url is None:
            base_url = os.environ.get("DFS_BASE_URL")
        if base_url is None:
            base_url = "https://api.dataforce.studio"

        super().__init__(base_url=base_url)

    @property
    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}

    # @cached_property
    @property
    @abstractmethod
    def organization(self) -> OrganizationResource:
        raise NotImplementedError()

    @property
    @abstractmethod
    def bucket_secret(self) -> BucketSecretResource:
        raise NotImplementedError()

    @property
    @abstractmethod
    def orbit(self) -> OrbitResource:
        raise NotImplementedError()

    @property
    @abstractmethod
    def collection(self) -> CollectionResource:
        raise NotImplementedError()

    @property
    @abstractmethod
    def ml_model(self) -> MLModelResource:
        raise NotImplementedError()

    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncDataForceClient(DataForceClientBase, AsyncBaseClient):
    @property
    def organization(self) -> AsyncOrganizationResource:
        from .resources.organizations import AsyncOrganizationResource

        return AsyncOrganizationResource(self)

    @property
    def bucket_secret(self) -> AsyncBucketSecretResource:
        from .resources.bucket_secrets import AsyncBucketSecretResource

        return AsyncBucketSecretResource(self)

    @property
    def orbit(self) -> AsyncOrbitResource:
        from .resources.orbits import AsyncOrbitResource

        return AsyncOrbitResource(self)

    @property
    def collection(self) -> AsyncCollectionResource:
        from .resources.collections import AsyncCollectionResource

        return AsyncCollectionResource(self)

    @property
    def ml_model(self) -> AsyncMLModelResource:
        from .resources.ml_models import AsyncMLModelResource

        return AsyncMLModelResource(self)


class DataForceClient(DataForceClientBase, SyncBaseClient):
    @property
    def organization(self) -> OrganizationResource:
        from .resources.organizations import OrganizationResource

        return OrganizationResource(self)

    @property
    def bucket_secret(self) -> BucketSecretResource:
        from .resources.bucket_secrets import BucketSecretResource

        return BucketSecretResource(self)

    @property
    def orbit(self) -> OrbitResource:
        from .resources.orbits import OrbitResource

        return OrbitResource(self)

    @property
    def collection(self) -> CollectionResource:
        from .resources.collections import CollectionResource

        return CollectionResource(self)

    @property
    def ml_model(self) -> MLModelResource:
        from .resources.ml_models import MLModelResource

        return MLModelResource(self)
