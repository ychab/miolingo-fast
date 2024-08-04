from typing import AsyncGenerator

from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    AsyncTransaction,
    create_async_engine,
)

import pytest

from miolingo import settings
from miolingo.conf.loggers import configure_loggers
from miolingo.db.base import Base
from miolingo.db.session import async_session_factory

from tests.factories.base import BaseFactory


@pytest.hookimpl(trylast=True)
def pytest_sessionstart() -> None:
    # Reconfigure loggers again to propagate logs to root logger, the only one captured by pytest(?)
    configure_loggers(handlers=settings.LOG_HANDLERS, level=settings.LOG_LEVEL, propagate=True)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    @see https://anyio.readthedocs.io/en/stable/testing.html#using-async-fixtures-with-higher-scopes
    """
    return "asyncio"


@pytest.fixture(scope="session")
def test_db_name() -> str:
    return f"test_{settings.POSTGRES_DB}"


@pytest.fixture(scope="session")
async def create_database(anyio_backend: str, test_db_name: str) -> AsyncGenerator:
    # Establish a connection to the current DB with admin role.
    async_engine_admin: AsyncEngine = create_async_engine(
        url=str(settings.POSTGRES_URI),
        isolation_level="AUTOCOMMIT",
    )
    # Then drop/create test database
    async with async_engine_admin.begin() as async_conn:
        await async_conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
        await async_conn.execute(text(f"CREATE DATABASE {test_db_name}"))

    yield

    # Finally drop the test database
    async with async_engine_admin.begin() as async_conn:
        await async_conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))


@pytest.fixture(scope="session")
async def async_engine(anyio_backend, create_database, test_db_name: str) -> AsyncGenerator[AsyncEngine, None]:
    url = make_url(str(settings.POSTGRES_URI)).set(database=test_db_name)
    async_engine = create_async_engine(url=url)
    yield async_engine
    await async_engine.dispose()


@pytest.fixture(scope="session")
async def async_connection(async_engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:
    async_conn: AsyncConnection = await async_engine.connect()
    yield async_conn
    await async_conn.close()


@pytest.fixture(scope="session")
async def create_tables(async_connection: AsyncConnection) -> AsyncGenerator:
    await async_connection.run_sync(Base.metadata.create_all)
    await async_connection.commit()
    yield
    await async_connection.run_sync(Base.metadata.drop_all)
    await async_connection.commit()


@pytest.fixture(scope="function", autouse=True)
async def async_session_db(create_tables, async_connection: AsyncConnection) -> AsyncGenerator[AsyncSession, None]:
    """
    @see https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    """
    # Begin a non-ORM transaction.
    async_transaction: AsyncTransaction = await async_connection.begin()

    # Reconfigure sessionmakers to use testing DB with root transaction started.
    async_session_factory.configure(bind=async_connection, join_transaction_mode="create_savepoint")

    async_session_db: AsyncSession = async_session_factory()
    BaseFactory.__async_session__ = async_session_db

    yield async_session_db

    await async_transaction.rollback()  # rollback everything
