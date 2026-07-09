class TestSustainabilityEndpoint:
    def test_get_sustainability(self, client):
        response = client.get("/api/v1/sustainability/")
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "ai_recommendation" in data
        assert isinstance(data["metrics"], list)
