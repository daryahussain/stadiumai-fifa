class TestCrowdEndpoint:
    def test_get_crowd_data(self, client):
        response = client.get("/api/v1/crowd/")
        assert response.status_code == 200
        data = response.json()
        assert "overview" in data
        assert "zones" in data
        assert "queues" in data
        assert "ai_summary" in data

        overview = data["overview"]
        assert "total_occupancy" in overview
        assert "congestion_level" in overview
        assert overview["congestion_level"] in ["low", "moderate", "high", "critical", "clear"]

        assert isinstance(data["zones"], list)
        assert isinstance(data["queues"], list)
