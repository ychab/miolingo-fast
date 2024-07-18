import uuid
from typing import AsyncGenerator

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from miolingo import settings
from miolingo.deps.users import get_user_db
from miolingo.models.users import User
from miolingo.schemas.users import UserCreate
from miolingo.utils.mails import send_mail_with_template
from miolingo.utils.urls import build_frontend_url


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET

    async def validate_password(self, password: str, user: UserCreate | User) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(reason="Password should be at least 8 characters")
        if user.email in password:
            raise InvalidPasswordException(reason="Password should not contain e-mail")

    async def on_after_request_verify(self, user: User, token: str, request: Request | None = None) -> None:
        await send_mail_with_template(
            subject="Verify your account",
            recipients=[user.email],
            template_name="users/request_verify.html",
            template_body={
                "fullname": user.fullname,
                "verify_link": build_frontend_url(
                    path=settings.FRONTEND_URL_VERIFY,
                    query={"token": token},
                ),
            },
        )

    async def on_after_forgot_password(self, user: User, token: str, request: Request | None = None) -> None:
        await send_mail_with_template(
            subject="Reset your password",
            recipients=[user.email],
            template_name="users/reset_password.html",
            template_body={
                "fullname": user.fullname,
                "reset_password_link": build_frontend_url(
                    path=settings.FRONTEND_URL_RESET_PASSWORD,
                    query={"token": token},
                ),
            },
        )


async def get_user_manager(user: SQLAlchemyUserDatabase = Depends(get_user_db)) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user)
