import secrets

from fastapi_users.password import PasswordHelper

from polyfactory import Ignore, Use
from polyfactory.decorators import post_generated

from miolingo.models.users import AccessToken, User

from tests.factories.base import BaseFactory


class UserFactory(BaseFactory[User]):
    first_name = Use(BaseFactory.__faker__.first_name)
    last_name = Use(BaseFactory.__faker__.last_name)

    is_active = True
    is_superuser = False
    is_verified = True

    @post_generated
    @classmethod
    def hashed_password(cls) -> str:
        return PasswordHelper().hash("test")

    @post_generated
    @classmethod
    def email(cls, first_name: str, last_name: str) -> str:
        return f"{first_name}.{last_name}-{cls.__random__.randint(0, 10000)}@miolingo.com"


class UserFactoryRel(UserFactory):
    __set_as_default_factory_for_type__ = False
    __set_relationships__ = True


class AccessTokenFactory(BaseFactory[AccessToken]):
    __set_relationships__ = True

    user = UserFactory
    created_at = Ignore()  # Default to DB now_utc

    @classmethod
    def token(cls) -> str:
        return secrets.token_urlsafe()
