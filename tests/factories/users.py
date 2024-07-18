from fastapi_users.password import PasswordHelper

import factory

from miolingo import settings
from miolingo.models.users import AccessToken, User
from tests.factories.base import BaseFactory

current_locale = settings.LANGUAGE_CODE


class UserFactory(BaseFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name", locale=current_locale)
    last_name = factory.Faker("last_name", locale=current_locale)
    email = factory.LazyAttributeSequence(lambda o, n: f"test-{n}+{o.first_name}.{o.last_name}@miolingo.com")

    is_active = True
    is_superuser = False
    is_verified = True

    @factory.lazy_attribute
    def hashed_password(self) -> str:
        return PasswordHelper().hash("test")

    @factory.post_generation
    def access_token(self, created, extracted, **kwargs) -> None:
        if created and extracted:  # pragma: no branch
            AccessTokenFactory(user=self)


class AccessTokenFactory(BaseFactory):
    class Meta:
        model = AccessToken

    user = factory.SubFactory(UserFactory)
