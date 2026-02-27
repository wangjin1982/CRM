"""AI模块冒烟测试"""
import pytest

from app.api.deps import get_current_user_id, get_db
from app.services.ai import AIService


@pytest.mark.asyncio
async def test_ai_query_requires_auth(app, client):
    async def fake_get_db():
        yield object()

    app.dependency_overrides[get_db] = fake_get_db
    resp = await client.post("/api/v1/ai/query", json={"query": "高风险商机有哪些"})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_ai_query_with_dependency_overrides(app, client, monkeypatch):
    async def fake_get_db():
        yield object()

    async def fake_nl_query(db, *, query, user_id):
        return {
            "intent": "mock",
            "answer": f"mock:{query}",
            "result_count": 1,
            "sql": "SELECT 1",
        }

    app.dependency_overrides[get_db] = fake_get_db
    app.dependency_overrides[get_current_user_id] = lambda: 1
    monkeypatch.setattr(AIService, "natural_language_query", fake_nl_query)

    resp = await client.post("/api/v1/ai/query", json={"query": "测试问题"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["answer"] == "mock:测试问题"
