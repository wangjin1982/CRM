"""路由契约测试"""


def test_core_routes_registered(app):
    paths = {route.path for route in app.routes if hasattr(route, "path")}

    required_paths = {
        "/api/v1/auth/login",
        "/api/v1/customers",
        "/api/v1/opportunities",
        "/api/v1/activity/visits",
        "/api/v1/activity/statistics",
        "/api/v1/ai/query",
        "/api/v1/ai/risk/batch-scan",
        "/api/v1/analytics/dashboard/home",
        "/api/v1/analytics/reports/{report_id}/execute",
    }

    missing = sorted(required_paths - paths)
    assert not missing, f"缺少路由: {missing}"
