from unittest.mock import AsyncMock

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.application import create_app
from app.core.settings import AppConfig
from app.dao.session_maker import session_manager


mock_session = AsyncMock(autospec=AsyncSession)


async def mock_get_session():
    # Мок для получения сессии без транзакции
    try:
        yield mock_session
        await mock_session.commit()
    finally:
        await mock_session.close()


async def mock_get_transaction_session():
    # Мок для получения сессии с управлением транзакцией
    try:
        yield mock_session
        await mock_session.commit()
    finally:
        await mock_session.close()


@pytest_asyncio.fixture
async def _app():
    config = AppConfig()
    app = create_app(config)

    # Переопределяем Depends[SessionDep]
    app.dependency_overrides[session_manager.get_session] = mock_get_session

    # Переопределяем Depends[TransactionSessionDep]
    app.dependency_overrides[session_manager.get_transaction_session] = mock_get_transaction_session

    return app


# todo: lifespan + transport=ASGITransport (на новых версиях)
@pytest_asyncio.fixture
async def client(_app):
    lifespan = LifespanManager(_app)
    httpx_client = AsyncClient(transport=ASGITransport(app=_app), base_url="http://testserver")
    async with httpx_client as client, lifespan:
        yield client
