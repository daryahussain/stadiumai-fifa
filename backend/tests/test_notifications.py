class TestNotificationEndpoint:
    def test_get_notifications(self, client):
        response = client.get("/api/v1/notifications/")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        assert isinstance(data["unread_count"], int)

    def test_mark_read(self, client):
        response = client.post("/api/v1/notifications/1/read")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
