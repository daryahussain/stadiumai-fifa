class TestTransportEndpoint:
    def test_get_transport(self, client):
        response = client.get("/api/v1/transport/")
        assert response.status_code == 200
        data = response.json()
        assert "options" in data
        assert "parking" in data
        assert "ai_recommendation" in data
        assert isinstance(data["options"], list)
        assert isinstance(data["parking"], list)
