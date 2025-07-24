import uuid

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from dataforce_studio.repositories.users import UserRepository
from dataforce_studio.schemas.user import (
    AuthProvider,
    CreateUser,
    UpdateUserAPIKey,
)


@pytest.mark.asyncio
async def test_create_user_api_key(
    create_database_and_apply_migrations: str,
) -> None:
    engine = create_async_engine(create_database_and_apply_migrations)
    user_repo = UserRepository(engine)

    user = CreateUser(
        email=f"test_create_user_api_key_{uuid.uuid4()}@email.com",
        full_name="Test User",
        disabled=False,
        email_verified=True,
        auth_method=AuthProvider.EMAIL,
        photo=None,
        hashed_password="hashed_password",
    )

    created_user = await user_repo.create_user(user)

    api_key_update = UpdateUserAPIKey(id=created_user.id, hashed_api_key="api_key_hash")
    result = await user_repo.create_user_api_key(api_key_update)

    assert created_user
    assert result is True


@pytest.mark.asyncio
async def test_get_user_by_api_key_hash(
    create_database_and_apply_migrations: str,
) -> None:
    engine = create_async_engine(create_database_and_apply_migrations)
    user_repo = UserRepository(engine)

    user = CreateUser(
        email=f"test_get_user_{uuid.uuid4()}@email.com",
        full_name="Test User",
        disabled=False,
        email_verified=True,
        auth_method=AuthProvider.EMAIL,
        photo=None,
        hashed_password="hashed_password",
    )

    created_user = await user_repo.create_user(user)

    api_key_hash = f"test_api_key_hash_{uuid.uuid4()}"
    api_key_update = UpdateUserAPIKey(id=created_user.id, hashed_api_key=api_key_hash)
    await user_repo.create_user_api_key(api_key_update)

    fetched_user = await user_repo.get_user_by_api_key_hash(api_key_hash)

    assert fetched_user
    assert fetched_user.id == created_user.id
    assert fetched_user.has_api_key is True


@pytest.mark.asyncio
async def test_delete_api_key_by_user_id(
    create_database_and_apply_migrations: str,
) -> None:
    engine = create_async_engine(create_database_and_apply_migrations)
    user_repo = UserRepository(engine)

    user = CreateUser(
        email=f"test_delete_api_key{uuid.uuid4()}@email.com",
        full_name="Test User",
        disabled=False,
        email_verified=True,
        auth_method=AuthProvider.EMAIL,
        photo=None,
        hashed_password="hashed_password",
    )

    created_user = await user_repo.create_user(user)
    key_hash = f"api_key_hash_{uuid.uuid4()}"

    api_key_update = UpdateUserAPIKey(id=created_user.id, hashed_api_key=key_hash)
    await user_repo.create_user_api_key(api_key_update)

    user_with_key = await user_repo.get_public_user_by_id(created_user.id)
    assert user_with_key.has_api_key is True

    await user_repo.delete_api_key_by_user_id(created_user.id)

    user_without_key = await user_repo.get_public_user_by_id(created_user.id)
    assert user_without_key.has_api_key is False

    fetched_user = await user_repo.get_user_by_api_key_hash(key_hash)
    assert fetched_user is None
