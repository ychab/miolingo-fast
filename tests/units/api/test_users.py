from fastapi_users.router import ErrorCode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from miolingo.models import User
from tests.factories.users import UserFactory
from tests.utils.client import AsyncClientTest


async def test_user_register(async_session_db: AsyncSession, async_client: AsyncClientTest) -> None:
    data_json = {
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": "jeandupont@miolingo.com",
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


async def test_user_register_invalid_password_too_short(async_client: AsyncClientTest) -> None:
    response = await async_client.post(
        url=async_client.url_path_for("register:register"),
        json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jeandupont@miolingo.com",
            "password": "test",  # too short
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == ErrorCode.REGISTER_INVALID_PASSWORD
    assert data["detail"]["reason"] == "Password should be at least 8 characters"


async def test_user_register_invalid_password_email(async_client: AsyncClientTest) -> None:
    response = await async_client.post(
        url=async_client.url_path_for("register:register"),
        json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jeandupont@miolingo.com",
            "password": "jeandupont@miolingo.com",  # Not an email!
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == ErrorCode.REGISTER_INVALID_PASSWORD
    assert data["detail"]["reason"] == "Password should not contain e-mail"


async def test_user_register_already_exists(scoped_session_db: Session, async_client: AsyncClientTest) -> None:
    user = UserFactory(email="jeandupont@miolingo.com")

    response = await async_client.post(
        url=async_client.url_path_for("register:register"),
        json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": user.email,
            "password": "testtest",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == ErrorCode.REGISTER_USER_ALREADY_EXISTS


# async def test_user_on_after_request_verify(async_client: AsyncClientTest):
#     user = UserFactory(is_superuser=True, email="foo@foo.com", hashed_password="nuihreuihg")
#     # assert user.id is not None
#     # await async_session_db.refresh(user)
#     assert user.id is not None
#
#
# async def test_user_on_after_forgot_password(async_session_db: AsyncSession, async_client: AsyncClientTest):
#     user = UserFactory(is_superuser=True, email="foo@foo.com", hashed_password="nuihreuihg")
#     assert user.id is not None
