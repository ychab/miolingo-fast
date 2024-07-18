from typing import AsyncGenerator, Generator

from sqlalchemy import Connection, Engine, Transaction, create_engine, make_url, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    AsyncTransaction,
    create_async_engine,
)
from sqlalchemy.orm import Session

import pytest

from miolingo import settings
from miolingo.conf.loggers import configure_loggers
from miolingo.db.base import Base
from miolingo.db.session import async_session_factory
from tests.utils.client import AsyncClientTest
from tests.utils.session import session_scoped


@pytest.hookimpl(trylast=True)
def pytest_sessionstart() -> None:
    # Reconfigure loggers again to propagate logs to root logger, the only one captured by pytest(?)
    configure_loggers(handlers=settings.LOG_HANDLERS, level=settings.LOG_LEVEL, propagate=True)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Redeclare anyio_backend fixture, but at scope session level.
    """
    return "asyncio"


@pytest.fixture(scope="session")
def test_db_name() -> str:
    return f"test_{settings.POSTGRES_DB}"


@pytest.fixture(scope="session")
async def create_database(anyio_backend, test_db_name: str) -> AsyncGenerator:
    # Establish a connection to the current DB with admin role.
    async_engine_admin: AsyncEngine = create_async_engine(
        url=str(settings.POSTGRES_URI_ASYNC),
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
def engine(create_database, test_db_name: str) -> Generator[Engine, None, None]:
    url = make_url(str(settings.POSTGRES_URI)).set(database=test_db_name)
    engine = create_engine(url=url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
async def async_engine(anyio_backend, create_database, test_db_name: str) -> AsyncGenerator[AsyncEngine, None]:
    url = make_url(str(settings.POSTGRES_URI_ASYNC)).set(database=test_db_name)
    async_engine = create_async_engine(url=url)
    yield async_engine
    await async_engine.dispose()


@pytest.fixture(scope="session")
async def create_tables(async_engine: AsyncEngine) -> AsyncGenerator:
    async with async_engine.begin() as async_conn:
        await async_conn.run_sync(Base.metadata.create_all)

    yield

    async with async_engine.begin() as async_conn:
        await async_conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function", autouse=True)
def scoped_session_db(create_tables, engine: Engine) -> Generator[Session, None, None]:
    conn: Connection = engine.connect()
    transaction: Transaction = conn.begin()
    # Reconfigure factory boy scoped session to use testing DB with transaction.
    session_scoped.configure(bind=conn)

    session_db: Session = session_scoped()

    yield session_db

    transaction.rollback()
    session_scoped.remove()
    conn.close()


@pytest.fixture(scope="function", autouse=True)
async def async_session_db(scoped_session_db: Session, async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_conn: AsyncConnection = await async_engine.connect()
    async_transaction: AsyncTransaction = await async_conn.begin()
    # Reconfigure app session maker to use testing DB with transaction started.
    async_session_factory.configure(bind=async_conn)

    async_session: AsyncSession = async_session_factory()
    yield async_session

    await async_transaction.rollback()
    await async_conn.close()


@pytest.fixture
async def async_client(async_session_db: AsyncSession) -> AsyncClientTest:
    return AsyncClientTest()
