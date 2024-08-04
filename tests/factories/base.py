from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory, T

from miolingo import settings


class BaseFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __use_defaults__ = True
    __set_as_default_factory_for_type__ = True
    __faker__ = Faker(locale=settings.LANGUAGE_CODE)
