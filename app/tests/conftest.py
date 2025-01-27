from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.application import create_app
from app.core.settings import AppConfig
from app.dependencies.dao_dep import get_session_with_commit, get_session_without_commit

mock_session = AsyncMock(autospec=AsyncSession)


async def mock_get_session_with_commit():
    # Мок для получения сессии без транзакции
    try:
        yield mock_session
        await mock_session.commit()
    finally:
        await mock_session.close()


async def mock_get_session_without_commit():
    # Мок для получения сессии с управлением транзакцией
    try:
        yield mock_session
    finally:
        await mock_session.close()


@pytest_asyncio.fixture
async def _app():
    config = AppConfig()
    app = create_app(config)

    # Переопределяем Depends[SessionDep]
    app.dependency_overrides[get_session_with_commit] = mock_get_session_with_commit

    # Переопределяем Depends[TransactionSessionDep]
    app.dependency_overrides[get_session_without_commit] = mock_get_session_without_commit

    return app


# todo: lifespan + transport=ASGITransport (на новых версиях)
@pytest_asyncio.fixture
async def client(_app):
    lifespan = LifespanManager(_app)
    httpx_client = AsyncClient(transport=ASGITransport(app=_app), base_url="http://testserver")
    async with httpx_client as client, lifespan:
        yield client


@pytest.fixture
def mock_db_session():
    return mock_session
