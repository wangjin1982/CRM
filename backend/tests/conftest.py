"""测试公共夹具"""
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import app as fastapi_app  # noqa: E402


@pytest.fixture
def app():
    return fastapi_app


@pytest.fixture(autouse=True)
def clear_dependency_overrides(app):
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
