from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

import pytest

from miolingo.models import User
from tests.factories.users import UserFactory
from tests.utils.client import AsyncClientTest

TEST_EMAIL: str = "test@miolingo.com"


def test_factory_create(scoped_session_db: Session) -> None:
    # First create an instance into DB with sync connector.
    user = UserFactory(email=TEST_EMAIL)
    assert user.id is not None

    # By the way, play a little with the scoped session provided.
    user_db = scoped_session_db.get(User, user.id)
    assert user_db.email == TEST_EMAIL
    assert user == user_db

    # Play again with the ORM just for memory.
    assert scoped_session_db.query(User).count() == 1
    assert scoped_session_db.query(User).first().email == TEST_EMAIL


def test_factory_create_rollback_no_duplicate(scoped_session_db: Session) -> None:
    """
    Because user email is unique, we check that previous user factory created
    is rollback properly (i.e: doesn't exists anymore in DB).
    """
    user = UserFactory(email=TEST_EMAIL)
    assert user.id is not None


def test_factory_create_duplicate(scoped_session_db: Session) -> None:
    user = UserFactory(email=TEST_EMAIL)
    assert user.id is not None

    with pytest.raises(IntegrityError):
        UserFactory(email=TEST_EMAIL)


async def test_api_rollback(async_session_db: AsyncSession, async_client: AsyncClientTest) -> None:
    data_json = {
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": TEST_EMAIL,
        "password": "testtest",
    }

    response = await async_client.post(
        url=async_client.url_path_for("register:register"),
        json=data_json,
    )

    assert response.status_code == 201
    data = response.json()

    assert data["first_name"] == data_json["first_name"]
    assert data["last_name"] == data_json["last_name"]
    assert data["email"] == data_json["email"]
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    assert data["is_verified"] is False

    user = await async_session_db.get(User, data["id"])
    assert str(user.id) == data["id"]


def test_api_rollback_no_duplicate(scoped_session_db: Session) -> None:
    """
    Because user email is unique, we check that previous API creation
    is rollback properly (i.e: doesn't exists anymore in DB).
    """
    user = UserFactory(email=TEST_EMAIL)
    assert user.id is not None
