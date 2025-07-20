import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from dataforce_studio.repositories.api_keys import APIKeyRepository
from dataforce_studio.repositories.users import UserRepository
from dataforce_studio.schemas.api_keys import (
    APIKeyAuthOut,
    APIKeyCreate,
    APIKeyCreateOut,
    APIKeyOut,
)
from dataforce_studio.schemas.user import (
    AuthProvider,
    CreateUser,
)


@pytest.mark.asyncio
async def test_create_user_api_key(
    create_database_and_apply_migrations: str,
) -> None:
    engine = create_async_engine(create_database_and_apply_migrations)
    user_repo = UserRepository(engine)
    api_keys_repo = APIKeyRepository(engine)

    user = CreateUser(
        email="test_create_user_api_key@email.com",
        full_name="Test User",
        disabled=False,
        email_verified=True,
        auth_method=AuthProvider.EMAIL,
        photo=None,
        hashed_password="hashed_password",
    )

    created_user = await user_repo.create_user(user)

    api_key = APIKeyCreate(user_id=created_user.id, hash="api_key_hash")
    created_api_key = await api_keys_repo.create_api_key(api_key)

    assert created_user
    assert created_api_key
    assert isinstance(created_api_key, APIKeyCreateOut)
    assert created_api_key.user_id == api_key.user_id


@pytest.mark.asyncio
async def test_get_api_key_by_user_id(
    create_database_and_apply_migrations: str,
) -> None:
    engine = create_async_engine(create_database_and_apply_migrations)
    user_repo = UserRepository(engine)
    api_keys_repo = APIKeyRepository(engine)

    user = CreateUser(
        email="test_get_api_key_by_user_id@email.com",
        full_name="Test User",
        disabled=False,
        email_verified=True,
        auth_method=AuthProvider.EMAIL,
        photo=None,
        hashed_password="hashed_password",
    )

    created_user = await user_repo.create_user(user)

    api_key = APIKeyCreate(user_id=created_user.id, hash="api_key_hash")

    await api_keys_repo.create_api_key(api_key)
    fetched_api_key = await api_keys_repo.get_api_key_by_user_id(created_user.id)

    assert fetched_api_key
    assert isinstance(fetched_api_key, APIKeyOut)
    assert fetched_api_key.user_id == created_user.id


@pytest.mark.asyncio
async def test_get_api_key_by_hash(
    create_database_and_apply_migrations: str,
) -> None:
    engine = create_async_engine(create_database_and_apply_migrations)
    user_repo = UserRepository(engine)
    api_keys_repo = APIKeyRepository(engine)

    user = CreateUser(
        email="get_api_key_by_hash@email.com",
        full_name="Test User",
        disabled=False,
        email_verified=True,
        auth_method=AuthProvider.EMAIL,
        photo=None,
        hashed_password="hashed_password",
    )

    created_user = await user_repo.create_user(user)

    api_key = APIKeyCreate(
        user_id=created_user.id, hash="api_key_hash_test_get_api_key_by_hash"
    )

    await api_keys_repo.create_api_key(api_key)
    fetched_api_key = await api_keys_repo.get_api_key_by_hash(api_key.hash)

    assert fetched_api_key
    assert isinstance(fetched_api_key, APIKeyAuthOut)
    assert fetched_api_key.user


@pytest.mark.asyncio
async def test_delete_api_key_by_user_id(
    create_database_and_apply_migrations: str,
) -> None:
    engine = create_async_engine(create_database_and_apply_migrations)
    user_repo = UserRepository(engine)
    api_keys_repo = APIKeyRepository(engine)

    user = CreateUser(
        email="test_delete_api_key_by_user_id@email.com",
        full_name="Test User",
        disabled=False,
        email_verified=True,
        auth_method=AuthProvider.EMAIL,
        photo=None,
        hashed_password="hashed_password",
    )

    created_user = await user_repo.create_user(user)

    api_key = APIKeyCreate(user_id=created_user.id, hash="api_key_hash")

    created_api_key = await api_keys_repo.create_api_key(api_key)

    await api_keys_repo.delete_api_key_by_user_id(created_user.id)
    fetched_api_key = await api_keys_repo.get_api_key_by_user_id(
        created_api_key.user_id
    )

    assert fetched_api_key is None
