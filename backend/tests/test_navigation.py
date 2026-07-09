import uuid
from app.models.route import Route


class TestNavigationEndpoint:
    def test_get_route(self, client, db_session):
        route = Route(
            id=uuid.uuid4(),
            stadium_id=uuid.uuid4(),
            name="Gate A → Section 100",
            start_location="Gate A",
            end_location="Section 100",
            distance_km=0.3,
            wheelchair_accessible="yes",
        )
        db_session.add(route)
        db_session.commit()

        response = client.post("/api/v1/navigation/route", json={
            "from_location": "Gate A",
            "to_location": "Section 100",
            "wheelchair": False,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["from_location"] == "Gate A"
        assert data["to_location"] == "Section 100"
        assert len(data["steps"]) > 0
        assert data["estimated_minutes"] > 0

    def test_get_route_not_found(self, client):
        response = client.post("/api/v1/navigation/route", json={
            "from_location": "Invalid",
            "to_location": "Nowhere",
            "wheelchair": False,
        })
        assert response.status_code == 404

    def test_get_route_wheelchair(self, client, db_session):
        route = Route(
            id=uuid.uuid4(),
            stadium_id=uuid.uuid4(),
            name="Gate A → Section 100",
            start_location="Gate A",
            end_location="Section 100",
            distance_km=0.3,
            wheelchair_accessible="yes",
        )
        db_session.add(route)
        db_session.commit()

        response = client.post("/api/v1/navigation/route", json={
            "from_location": "Gate A",
            "to_location": "Section 100",
            "wheelchair": True,
        })
        assert response.status_code == 200
        assert response.json()["wheelchair_accessible"] is True

    def test_get_navigation_data(self, client, db_session):
        route = Route(
            id=uuid.uuid4(),
            stadium_id=uuid.uuid4(),
            name="Test Route",
            start_location="Gate A",
            end_location="Section 100",
            distance_km=0.3,
            wheelchair_accessible="yes",
        )
        db_session.add(route)
        db_session.commit()

        response = client.get("/api/v1/navigation/data")
        assert response.status_code == 200
        data = response.json()
        assert "zones" in data
        assert "gates" in data
        assert "amenities" in data
        assert "Gate A" in data["zones"]
