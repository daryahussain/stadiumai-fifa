import uuid
from app.models.chat_history import ChatHistory


class TestChatEndpoint:
    def test_send_message(self, client, db_session):
        response = client.post("/api/v1/chat/message", json={
            "session_id": str(uuid.uuid4()),
            "message": "Hello, what can you help me with?",
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["message"]["role"] == "assistant"
        assert len(data["message"]["content"]) > 0

        messages = db_session.query(ChatHistory).all()
        assert len(messages) >= 2

    def test_send_message_without_session(self, client, db_session):
        response = client.post("/api/v1/chat/message", json={
            "message": "Where is Gate A?",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] is not None

    def test_get_history(self, client, db_session):
        session_id = str(uuid.uuid4())
        client.post("/api/v1/chat/message", json={
            "session_id": session_id,
            "message": "Test message",
        })
        response = client.get(f"/api/v1/chat/history/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) >= 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][-1]["role"] == "assistant"

    def test_get_empty_history(self, client):
        response = client.get("/api/v1/chat/history/nonexistent-session")
        assert response.status_code == 200
        assert response.json()["messages"] == []

    def test_smart_fallback_greeting(self, client):
        response = client.post("/api/v1/chat/message", json={
            "message": "Hello",
        })
        assert response.status_code == 200
        content = response.json()["message"]["content"]
        assert "StadiumAI" in content or "Hello" in content or "help" in content

    def test_smart_fallback_seat(self, client):
        response = client.post("/api/v1/chat/message", json={
            "message": "Where is my seat?",
        })
        assert response.status_code == 200
        content = response.json()["message"]["content"]
        assert "Section" in content or "Gate" in content or "seat" in content.lower()

    def test_smart_fallback_food(self, client):
        response = client.post("/api/v1/chat/message", json={
            "message": "Where can I eat?",
        })
        assert response.status_code == 200
        content = response.json()["message"]["content"]
        assert any(x in content for x in ["Fan Favorites", "World Bites", "food", "eat"])

    def test_smart_fallback_parking(self, client):
        response = client.post("/api/v1/chat/message", json={
            "message": "Where should I park?",
        })
        assert response.status_code == 200
        content = response.json()["message"]["content"]
        assert "Lot" in content or "parking" in content.lower()

    def test_smart_fallback_transport(self, client):
        response = client.post("/api/v1/chat/message", json={
            "message": "How do I get to the stadium?",
        })
        assert response.status_code == 200
        content = response.json()["message"]["content"]
        assert any(x in content for x in ["Metro", "bus", "shuttle", "concourse", "Gates", "directions"])

    def test_smart_fallback_transport_options(self, client):
        response = client.post("/api/v1/chat/message", json={
            "message": "What transport options are available?",
        })
        assert response.status_code == 200
        content = response.json()["message"]["content"]
        assert any(x in content for x in ["Metro", "bus", "shuttle"])

    def test_smart_fallback_match(self, client):
        response = client.post("/api/v1/chat/message", json={
            "message": "When is the next match?",
        })
        assert response.status_code == 200
        content = response.json()["message"]["content"]
        assert "vs" in content or "match" in content.lower()

    def test_smart_fallback_emergency(self, client):
        response = client.post("/api/v1/chat/message", json={
            "message": "I need help, it's an emergency",
        })
        assert response.status_code == 200
        content = response.json()["message"]["content"]
        assert "Emergency" in content or "FIFA-HELP" in content or "emergency" in content.lower()

    def test_smart_fallback_capabilities(self, client):
        response = client.post("/api/v1/chat/message", json={
            "message": "What can you do?",
        })
        assert response.status_code == 200
        content = response.json()["message"]["content"]
        assert len(content) > 0

    def test_stream_endpoint_returns_events(self, client, db_session):
        response = client.post("/api/v1/chat/stream", json={
            "session_id": str(uuid.uuid4()),
            "message": "Hello",
        })
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        body = response.text
        assert "data:" in body
        assert "done" in body or "token" in body

    def test_stream_saves_to_db(self, client, db_session):
        session_id = str(uuid.uuid4())
        response = client.post("/api/v1/chat/stream", json={
            "session_id": session_id,
            "message": "Where is my seat?",
        })
        assert response.status_code == 200
        messages = db_session.query(ChatHistory).filter(
            ChatHistory.session_id == session_id
        ).all()
        assert len(messages) >= 2
        roles = [m.role for m in messages]
        assert "user" in roles
        assert "assistant" in roles

    def test_fallback_without_db(self, client):
        """Basic fallback should work even without seeded DB data."""
        response = client.post("/api/v1/chat/message", json={
            "message": "random question that doesn't match any intent",
        })
        assert response.status_code == 200
        assert len(response.json()["message"]["content"]) > 0

    def test_follow_up_question(self, client):
        """Simulate a follow-up question after first question."""
        session_id = str(uuid.uuid4())
        r1 = client.post("/api/v1/chat/message", json={
            "session_id": session_id,
            "message": "Where is my seat?",
        })
        assert r1.status_code == 200

        r2 = client.post("/api/v1/chat/message", json={
            "session_id": session_id,
            "message": "And what about food?",
        })
        assert r2.status_code == 200
        content = r2.json()["message"]["content"]
        assert len(content) > 0
