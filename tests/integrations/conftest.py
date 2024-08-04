from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

import pytest

from tests.utils.client import AsyncClientTest


@pytest.fixture
async def async_client(async_session_db: AsyncSession) -> AsyncClientTest:
    return AsyncClientTest()
