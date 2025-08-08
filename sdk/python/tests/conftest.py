import datetime
from typing import Any
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
import pytest_asyncio

from dataforce import AsyncDataForceClient, DataForceClient
from dataforce.api._types import (
    BucketSecret,
    Collection,
    ModelArtifact,
    Orbit,
    Organization,
)

TEST_BASE_URL = "http://127.0.0.1:8000"
TEST_API_KEY = "test-api-key"


@pytest.fixture
def mock_sync_client() -> Mock:
    client = Mock(spec=DataForceClient)
    client.organization = 1
    client.orbit = 1215
    client.collection = 15

    client.get = Mock()
    client.post = Mock()
    client.patch = Mock()
    client.delete = Mock()
    client.filter_none = Mock(
        side_effect=lambda x: {k: v for k, v in x.items() if v is not None}
    )

    return client


@pytest.fixture
def mock_async_client() -> AsyncMock:
    client = AsyncMock(spec=AsyncDataForceClient)
    client.organization = 1
    client.orbit = 1215
    client.collection = 15

    client.get = AsyncMock()
    client.post = AsyncMock()
    client.patch = AsyncMock()
    client.delete = AsyncMock()
    client.filter_none = Mock(
        side_effect=lambda x: {k: v for k, v in x.items() if v is not None}
    )

    return client


@pytest.fixture
def sample_organization_data() -> dict:
    return {"id": 1, "name": "Test Organization", "created_at": "2024-01-01T00:00:00Z"}


@pytest.fixture
def sample_orbit_data() -> dict:
    return {
        "id": 1215,
        "name": "Test Orbit",
        "organization_id": 1,
        "bucket_secret_id": 75,
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_collection_data() -> dict:
    return {
        "id": 15,
        "name": "Test Collection",
        "description": "Test collection description",
        "collection_type": "model",
        "orbit_id": 1215,
        "total_models": 0,
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_organization(sample_organization_data: dict) -> Organization:
    return Organization.model_validate(sample_organization_data)


@pytest.fixture
def sample_orbit(sample_orbit_data: dict) -> Orbit:
    return Orbit.model_validate(sample_orbit_data)


@pytest.fixture
def sample_collection(sample_collection_data: dict) -> Collection:
    return Collection.model_validate(sample_collection_data)


@pytest.fixture
def sample_bucket_secret() -> BucketSecret:
    return BucketSecret(
        id=75,
        endpoint="test.endpoint.com",
        bucket_name="test-bucket",
        organization_id=1,
        created_at=str(datetime.datetime.now()),
    )


@pytest.fixture
def sample_model_artifact() -> ModelArtifact:
    return ModelArtifact(
        id=2,
        file_name="model.pkl",
        model_name="test-model",
        collection_id=15,
        size=1024,
        file_hash="abc123",
        created_at=str(datetime.datetime.now()),
        metrics={},
        manifest={},
        file_index={},
        bucket_location="location",
        unique_identifier="unique_identifier",
        status="status",
    )


@pytest.fixture
def mock_initialization_requests(
    respx_mock: Any,  # noqa: ANN401
    sample_organization_data: dict,
    sample_orbit_data: dict,
    sample_collection_data: dict,
    sample_organization: Organization,
    sample_orbit: Orbit,
    sample_collection: Collection,
) -> dict:
    organization_id = sample_organization_data["id"]
    orbit_id = sample_orbit_data["id"]

    respx_mock.get("/users/me/organizations").mock(
        return_value=httpx.Response(200, json=[sample_organization_data])
    )

    respx_mock.get(f"/organizations/{organization_id}/orbits").mock(
        return_value=httpx.Response(200, json=[sample_orbit_data])
    )

    respx_mock.get(
        f"/organizations/{organization_id}/orbits/{orbit_id}/collections"
    ).mock(return_value=httpx.Response(200, json=[sample_collection_data]))

    return {
        "organization": sample_organization,
        "orbit": sample_orbit,
        "collection": sample_collection,
    }


@pytest.fixture
def client_with_mocks(mock_initialization_requests: dict) -> DataForceClient:
    return DataForceClient(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)


@pytest_asyncio.fixture
async def async_client_with_mocks(
    mock_initialization_requests: dict,
    sample_organization_data: dict,
    sample_orbit_data: dict,
    sample_collection_data: dict,
) -> AsyncDataForceClient:
    organization_id = sample_organization_data["id"]
    orbit_id = sample_orbit_data["id"]
    collection_id = sample_collection_data["id"]

    client = AsyncDataForceClient(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)
    await client.setup_config(
        organization=organization_id, orbit=orbit_id, collection=collection_id
    )
    return client
