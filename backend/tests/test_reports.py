class TestIncidentEndpoint:
    def test_report_incident(self, client):
        response = client.post("/api/v1/reports/incidents", json={
            "incident_type": "medical",
            "severity": 3,
            "description": "Someone needs help",
            "location": "Section 100",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["incident_type"] == "medical"
        assert data["severity"] == 3
        assert data["status"] == "reported"
        assert "ai_response" in data

    def test_report_invalid_type(self, client):
        response = client.post("/api/v1/reports/incidents", json={
            "incident_type": "invalid_type",
            "severity": 1,
            "description": "Test",
            "location": "Gate A",
        })
        assert response.status_code == 400

    def test_report_invalid_severity(self, client):
        response = client.post("/api/v1/reports/incidents", json={
            "incident_type": "fire",
            "severity": 6,
            "description": "Test",
            "location": "Gate A",
        })
        assert response.status_code == 400

    def test_get_incidents(self, client):
        response = client.get("/api/v1/reports/incidents")
        assert response.status_code == 200
        assert "incidents" in response.json()

    def test_severity_responses(self, client):
        for sev in range(1, 6):
            response = client.post("/api/v1/reports/incidents", json={
                "incident_type": "security",
                "severity": sev,
                "description": "Test",
                "location": "Gate A",
            })
            assert response.status_code == 200
            assert len(response.json()["ai_response"]) > 0
