import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory

from tests.utils.session import async_session_scoped


class BaseFactory(AsyncSQLAlchemyFactory):
    """
    @see https://factoryboy.readthedocs.io/en/stable/orms.html#sqlalchemy
    """
    class Meta:
        abstract = True
        sqlalchemy_session = async_session_scoped
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_COMMIT
