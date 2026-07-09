from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.models.user import User


class TestAuthEndpoints:
    def test_register(self, client, db_session):
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "test123",
            "full_name": "Test User",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

        user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert user is not None
        assert user.full_name == "Test User"

    def test_register_duplicate(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "password": "test123",
            "full_name": "Dup",
        })
        response = client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "password": "test123",
            "full_name": "Dup",
        })
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_login(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "login@example.com",
            "password": "pass123",
            "full_name": "Login User",
        })
        response = client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "pass123",
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_invalid(self, client, db_session):
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrong",
        })
        assert response.status_code == 401

    def test_me(self, client, db_session):
        reg = client.post("/api/v1/auth/register", json={
            "email": "me@example.com",
            "password": "pass123",
            "full_name": "Me User",
        })
        token = reg.json()["access_token"]

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"
        assert response.json()["full_name"] == "Me User"

    def test_me_unauthorized(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestSecurityUtils:
    def test_hash_and_verify(self):
        hashed = hash_password("mysecret")
        assert hashed != "mysecret"
        assert verify_password("mysecret", hashed)
        assert not verify_password("wrong", hashed)

    def test_create_and_decode_token(self):
        token = create_access_token({"sub": "user-123"})
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert "exp" in payload
