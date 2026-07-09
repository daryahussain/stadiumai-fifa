class TestDashboardEndpoint:
    def test_get_dashboard(self, client):
        response = client.get("/api/v1/dashboard/")
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "matches" in data
        assert "alerts" in data
        assert "crowd_trend" in data
        assert "ai_insight" in data

        assert len(data["stats"]) == 4
        assert len(data["crowd_trend"]) == 7
        assert data["ai_insight"] != ""
