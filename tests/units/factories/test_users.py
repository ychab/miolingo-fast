from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from miolingo.managers.users import UserManager
from miolingo.models import AccessToken, User
from tests.factories.users import AccessTokenFactory, UserFactory, UserFactoryRel

TEST_EMAIL: str = "test@miolingo.com"


async def test_user_factory(async_session_db: AsyncSession) -> None:
    user = await UserFactory.create_async()
    assert user.id is not None
    assert user.first_name is not None
    assert user.last_name is not None
    assert user.hashed_password is not None

    assert user.email is not None
    assert user.first_name in user.email
    assert user.last_name in user.email

    assert user.is_active is True
    assert user.is_superuser is False
    assert user.is_verified is True


async def test_user_factory_orm(async_session_db: AsyncSession) -> None:
    user = await UserFactory.create_async(email=TEST_EMAIL)
    assert user.id is not None

    # By the way, play a little with the scoped session provided.
    user_db = await async_session_db.get(User, user.id)
    assert user.id == user_db.id
    assert user_db.email == TEST_EMAIL

    # Play again with the ORM just for memory.
    count = await async_session_db.scalar(select(func.count(User.id)))
    assert count == 1

    first = await async_session_db.scalar(select(User).where(User.email == TEST_EMAIL))
    assert first.id == user.id
    assert first.email == TEST_EMAIL


async def test_user_factory_duplicate(async_session_db: AsyncSession) -> None:
    # First create an instance into DB with sync connector...
    user = await UserFactory.create_async(email=TEST_EMAIL)
    assert user.id is not None


async def test_user_factory_duplicate_none() -> None:
    # Then check that rollback is working
    user = await UserFactory.create_async(email=TEST_EMAIL)
    assert user.id is not None

    with pytest.raises(IntegrityError):
        await UserFactory.create_async(email=TEST_EMAIL)


async def test_user_factory_default_password() -> None:
    user = await UserFactory.create_async()
    assert user.id is not None

    assert UserManager(user).check_password(user, "test") is True


async def test_user_factory_refresh(async_session_db: AsyncSession) -> None:
    user = await UserFactory.create_async(email=TEST_EMAIL)
    assert user.id is not None

    user.email = "foo@miolingo.com"

    await async_session_db.refresh(user)
    assert user.email == TEST_EMAIL


async def test_user_factory_access_token_none(async_session_db: AsyncSession) -> None:
    user = await UserFactory.create_async(email=TEST_EMAIL)
    assert user.id is not None

    access_token = await user.awaitable_attrs.access_token
    assert access_token is None

    access_token_db = await async_session_db.scalar(select(AccessToken).where(AccessToken.user_id == user.id))
    assert access_token_db is None


async def test_user_factory_access_token(async_session_db: AsyncSession) -> None:
    user = await UserFactoryRel.create_async()
    assert user.id is not None

    access_token_db = await async_session_db.scalar(select(AccessToken).where(AccessToken.user_id == user.id))
    assert access_token_db is not None
    assert access_token_db.user_id == user.id


async def test_user_factory_access_token_relationship(async_session_db: AsyncSession) -> None:
    user = await UserFactoryRel.create_async()
    assert user.id is not None

    access_token = await user.awaitable_attrs.access_token
    assert access_token is not None
    assert access_token.token is not None
    assert access_token.user_id == user.id

    user_token = await access_token.awaitable_attrs.user
    assert user.id == user_token.id


async def test_access_token_factory(async_session_db: AsyncSession) -> None:
    access_token = await AccessTokenFactory.create_async()
    assert access_token.token is not None
    assert access_token.user_id is not None


async def test_access_token_factory_relationship(async_session_db: AsyncSession) -> None:
    access_token = await AccessTokenFactory.create_async()
    assert access_token.token is not None

    user = await access_token.awaitable_attrs.user
    assert user.id is not None
    assert access_token.user_id == user.id
