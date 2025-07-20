from unittest.mock import AsyncMock, patch
from datetime import datetime
import pytest

from dataforce_studio.handlers.api_keys import APIKeyHandler
from dataforce_studio.infra.exceptions import UserAPIKeyCreateError
from dataforce_studio.schemas.api_keys import APIKeyCreateOut, APIKeyCreate, APIKeyOut

handler = APIKeyHandler()


@patch(
    "dataforce_studio.handlers.api_keys.APIKeyRepository.create_api_key",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_create_user_api_key(
    mock_create_api_key: AsyncMock,
) -> None:
    user_id = 1
    expected = APIKeyCreateOut(
        user_id=user_id,
        created_at=datetime.now(),
        key="dfs_api_key_generated_info"
    )

    mock_create_api_key.return_value = expected

    actual = await handler.create_user_api_key(user_id)

    assert actual == expected
    mock_create_api_key.assert_awaited_once()


@patch(
    "dataforce_studio.handlers.api_keys.APIKeyRepository.create_api_key",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_create_user_api_key_already_exist(
    mock_create_api_key: AsyncMock,
) -> None:
    from dataforce_studio.infra.exceptions import DatabaseConstraintError
    
    user_id = 1
    
    mock_create_api_key.side_effect = DatabaseConstraintError("Key already exists")

    with pytest.raises(UserAPIKeyCreateError):
        await handler.create_user_api_key(user_id)


@patch(
    "dataforce_studio.handlers.api_keys.APIKeyRepository.get_api_key_by_user_id",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_get_user_api_key(
    mock_get_api_key_by_user_id: AsyncMock,
) -> None:
    user_id = 1
    expected = APIKeyOut(
        user_id=user_id,
        created_at=datetime.now(),
    )

    mock_get_api_key_by_user_id.return_value = expected

    actual = await handler.get_user_api_key(user_id)

    assert actual == expected
    mock_get_api_key_by_user_id.assert_awaited_once_with(user_id)



@patch(
    "dataforce_studio.handlers.api_keys.APIKeyRepository.get_api_key_by_user_id",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_get_user_api_key_not_found(
    mock_get_api_key_by_user_id: AsyncMock,
) -> None:
    user_id = 1

    mock_get_api_key_by_user_id.return_value = None

    actual = await handler.get_user_api_key(user_id)

    assert actual is None
    mock_get_api_key_by_user_id.assert_awaited_once_with(user_id)





@patch(
    "dataforce_studio.handlers.api_keys.APIKeyRepository.delete_api_key_by_user_id",
    new_callable=AsyncMock,
)
@patch(
    "dataforce_studio.handlers.api_keys.APIKeyRepository.get_api_key",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_delete_user_api_key(
    mock_get_api_key: AsyncMock,
    mock_delete_api_key_by_user_id: AsyncMock,
) -> None:
    user_id = 1
    expected = APIKeyOut(
        user_id=user_id,
        created_at=datetime.now(),
    )

    mock_get_api_key.return_value = expected

    await handler.delete_user_api_key(user_id)

    mock_get_api_key.assert_awaited_once_with(user_id)
    mock_delete_api_key_by_user_id.assert_awaited_once_with(user_id)


@patch(
    "dataforce_studio.handlers.api_keys.APIKeyRepository.get_api_key",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_delete_user_api_key_not_found(
    mock_get_api_key: AsyncMock,
) -> None:
    from dataforce_studio.infra.exceptions import APIKeyNotFoundError
    
    user_id = 1
    mock_get_api_key.return_value = None

    with pytest.raises(APIKeyNotFoundError):
        await handler.delete_user_api_key(user_id)

    mock_get_api_key.assert_awaited_once_with(user_id)


@patch(
    "dataforce_studio.handlers.api_keys.APIKeyRepository.create_api_key",
    new_callable=AsyncMock,
)
@patch(
    "dataforce_studio.handlers.api_keys.APIKeyRepository.delete_api_key_by_user_id",
    new_callable=AsyncMock,
)
@patch(
    "dataforce_studio.handlers.api_keys.APIKeyRepository.get_api_key",
    new_callable=AsyncMock,
)
@pytest.mark.asyncio
async def test_regenerate_user_api_key(
    mock_get_api_key: AsyncMock,
    mock_delete_api_key_by_user_id: AsyncMock,
    mock_create_api_key: AsyncMock,
) -> None:
    user_id = 1
    existing_key = APIKeyOut(
        user_id=user_id,
        created_at=datetime.now(),
    )
    expected = APIKeyCreateOut(
        user_id=user_id,
        created_at=datetime.now(),
        key="dfs_new_regenerated_key"
    )

    mock_get_api_key.return_value = existing_key
    mock_create_api_key.return_value = expected

    actual = await handler.regenerate_user_api_key(user_id)

    assert actual == expected
    mock_get_api_key.assert_awaited_once_with(user_id)
    mock_delete_api_key_by_user_id.assert_awaited_once_with(user_id)
    mock_create_api_key.assert_awaited_once()
