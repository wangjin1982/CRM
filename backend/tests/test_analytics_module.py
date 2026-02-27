"""分析模块冒烟测试"""
import pytest

from app.api.deps import get_current_user_id, get_db
from app.services.analytics import AnalyticsService


@pytest.mark.asyncio
async def test_dashboard_home_with_dependency_override(app, client, monkeypatch):
    async def fake_get_db():
        yield object()

    async def fake_dashboard_home(db):
        return {
            "summary": {
                "total_customers": 10,
                "total_open_opportunities": 5,
                "total_open_amount": 120000,
                "high_risk_opportunities": 1,
            },
            "updated_at": "2026-01-01T00:00:00",
        }

    app.dependency_overrides[get_db] = fake_get_db
    monkeypatch.setattr(AnalyticsService, "dashboard_home", fake_dashboard_home)

    resp = await client.get("/api/v1/analytics/dashboard/home")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["summary"]["total_customers"] == 10


@pytest.mark.asyncio
async def test_create_report_with_dependency_override(app, client, monkeypatch):
    class DummyReport:
        id = 101

    async def fake_get_db():
        yield object()

    async def fake_create_report(db, *, payload, user_id):
        assert payload["report_name"] == "测试报表"
        assert user_id == 1
        return DummyReport()

    app.dependency_overrides[get_db] = fake_get_db
    app.dependency_overrides[get_current_user_id] = lambda: 1
    monkeypatch.setattr(AnalyticsService, "create_report", fake_create_report)

    resp = await client.post(
        "/api/v1/analytics/reports",
        json={
            "report_name": "测试报表",
            "report_code": "test_report",
            "report_type": "customer",
            "config": {},
            "is_active": True,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 200
    assert body["data"]["id"] == 101
