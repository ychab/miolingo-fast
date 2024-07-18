import factory

from tests.utils.session import session_scoped


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    @see https://factoryboy.readthedocs.io/en/stable/orms.html#sqlalchemy
    """

    class Meta:
        sqlalchemy_session = session_scoped
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_COMMIT
