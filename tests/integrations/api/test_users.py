from email.message import Message
from urllib.parse import parse_qs, urlparse

from fastapi_users.router import ErrorCode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bs4 import BeautifulSoup

from miolingo.managers.users import UserManager
from miolingo.models import AccessToken, User
from miolingo.utils.mails import fast_mail

from tests.factories.users import UserFactory, UserFactoryRel
from tests.utils.client import AsyncClientTest
from tests.utils.mails import get_payload


async def test_user_register(async_session_db: AsyncSession, async_client: AsyncClientTest) -> None:
    payload = {
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": "jeandupont@miolingo.com",
        "password": "testtest",
    }

    response = await async_client.post(
        url=async_client.url_path_for("register:register"),
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]
    assert data["email"] == payload["email"]
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


async def test_user_register_already_exists(async_client: AsyncClientTest) -> None:
    user = await UserFactory.create_async(email="jeandupont@miolingo.com")

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
    assert data["detail"] == ErrorCode.REGISTER_USER_ALREADY_EXISTS


async def test_user_request_verify(async_session_db: AsyncSession, async_client: AsyncClientTest) -> None:
    user = await UserFactory.create_async(is_verified=False)
    assert user.is_verified is False

    # First request a token to verify the account.
    with fast_mail.record_messages() as outbox:
        response = await async_client.post(
            url=async_client.url_path_for("verify:request-token"),
            json={"email": user.email},
        )

    assert response.status_code == 202
    assert response.json() is None

    assert len(outbox) == 1
    msg: Message = outbox[0]
    payload = get_payload(msg)
    assert msg["Subject"] == "Verify your account"
    assert "?token=" in payload

    href = BeautifulSoup(payload, features="html.parser").find("a")["href"]
    token: str = parse_qs(urlparse(href).query)["token"][0]

    # Then request verification with the provided token by email.
    response = await async_client.post(
        url=async_client.url_path_for("verify:verify"),
        json={"token": token},
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(user.id)
    assert content["is_verified"] is True

    user = await async_session_db.get(User, user.id)
    assert user.is_verified is True


async def test_user_forgot_password(async_session_db: AsyncSession, async_client: AsyncClientTest) -> None:
    user = await UserFactory.create_async()

    # First request a token to verify the account.
    with fast_mail.record_messages() as outbox:
        response = await async_client.post(
            url=async_client.url_path_for("reset:forgot_password"),
            json={"email": user.email},
        )

    assert response.status_code == 202
    assert response.json() is None

    assert len(outbox) == 1
    msg: Message = outbox[0]
    payload = get_payload(msg)
    assert msg["Subject"] == "Reset your password"
    assert "?token=" in payload

    href = BeautifulSoup(payload, features="html.parser").find("a")["href"]
    token: str = parse_qs(urlparse(href).query)["token"][0]

    # Then request verification with the provided token by email.
    new_passwd = "adminadmin"
    response = await async_client.post(
        url=async_client.url_path_for("reset:reset_password"),
        json={
            "token": token,
            "password": new_passwd,
        },
    )
    assert response.status_code == 200
    assert response.json() is None

    user = await async_session_db.get(User, user.id)
    assert UserManager(user).check_password(user, new_passwd) is True


async def test_user_login(async_session_db: AsyncSession, async_client: AsyncClientTest) -> None:
    user = await UserFactory.create_async()

    access_token = await user.awaitable_attrs.access_token
    assert access_token is None

    response = await async_client.post(
        url=async_client.url_path_for("auth:database.login"),
        data={
            "username": user.email,
            "password": "test",
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert content["access_token"] is not None
    assert content["token_type"] == "bearer"

    access_token = await async_session_db.scalar(select(AccessToken).where(AccessToken.user_id == user.id))
    assert access_token is not None
    assert content["access_token"] == access_token.token


async def test_user_force_login(async_session_db: AsyncSession, async_client: AsyncClientTest) -> None:
    user = await UserFactoryRel.create_async()
    access_token = await user.awaitable_attrs.access_token

    async_client.force_login(access_token)

    response = await async_client.get(
        url=async_client.url_path_for("users:current_user"),
    )
    assert response.status_code == 200


async def test_user_force_logout(async_session_db: AsyncSession, async_client: AsyncClientTest) -> None:
    user = await UserFactoryRel.create_async()
    access_token = await user.awaitable_attrs.access_token

    async_client.force_login(access_token)
    assert "authorization" in async_client.headers

    async_client.force_logout()
    assert "authorization" not in async_client.headers

    response = await async_client.get(
        url=async_client.url_path_for("users:current_user"),
    )
    assert response.status_code == 401


async def test_user_me(async_session_db: AsyncSession, async_client: AsyncClientTest) -> None:
    user = await UserFactoryRel.create_async(is_superuser=True)
    access_token = await user.awaitable_attrs.access_token
    async_client.force_login(access_token)

    response = await async_client.get(
        url=async_client.url_path_for("users:current_user"),
    )
    assert response.status_code == 200
    content = response.json()

    assert content["id"] == str(user.id)
    assert content["first_name"] == user.first_name
    assert content["last_name"] == user.last_name
    assert content["email"] == user.email
    assert content["is_active"] is True
    assert content["is_superuser"] is True
    assert content["is_verified"] is True
