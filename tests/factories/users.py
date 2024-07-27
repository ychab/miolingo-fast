import secrets
from typing import Any

from fastapi_users.password import PasswordHelper

import factory

from miolingo import settings
from miolingo.models.users import AccessToken, User
from tests.factories.base import BaseFactory

current_locale = settings.LANGUAGE_CODE


class UserFactory(BaseFactory):
    class Meta:
        model = User

    class Params:
        password = "test"

    first_name = factory.Faker("first_name", locale=current_locale)
    last_name = factory.Faker("last_name", locale=current_locale)
    email = factory.LazyAttributeSequence(lambda o, n: f"test-{n}+{o.first_name}.{o.last_name}@miolingo.com")
    hashed_password = factory.LazyAttribute(lambda o: PasswordHelper().hash(o.password))

    is_active = True
    is_superuser = False
    is_verified = True

    @factory.post_generation
    def access_token(self, created, extracted, **kwargs) -> None:
        if created and extracted:  # pragma: no branch
            AccessTokenFactory(user=self)


class AccessTokenFactory(BaseFactory):
    class Meta:
        model = AccessToken

    user = factory.SubFactory(UserFactory)
