import pytest_asyncio
from app.db.session import engine


@pytest_asyncio.fixture(autouse=True)
async def cleanup_engine():
    yield
    await engine.dispose()
