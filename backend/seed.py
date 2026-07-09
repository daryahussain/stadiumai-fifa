"""Seed script to populate the database with initial data for FIFA World Cup 2026."""

import uuid
from datetime import datetime, timezone, timedelta

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models import (
    User, Stadium, Match, CrowdData, Route,
    Volunteer, Incident, Notification, ChatHistory, AIReport,
    TransportOption, ParkingLot, SustainabilityLog,
)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(User).first():
            print("Database already seeded — skipping.")
            return

        # --- Users ---
        admin = User(
            id=uuid.uuid4(),
            email="admin@stadiumai.com",
            hashed_password=hash_password("admin123"),
            full_name="Admin User",
            role="admin",
            is_active=True,
        )
        fan = User(
            id=uuid.uuid4(),
            email="fan@example.com",
            hashed_password=hash_password("fan123"),
            full_name="John Doe",
            role="fan",
            is_active=True,
        )
        staff = User(
            id=uuid.uuid4(),
            email="staff@stadiumai.com",
            hashed_password=hash_password("staff123"),
            full_name="Staff Member",
            role="staff",
            is_active=True,
        )
        db.add_all([admin, fan, staff])

        # --- Stadiums (FIFA World Cup 2026 host stadiums) ---
        stadiums_data = [
            {"name": "MetLife Stadium", "city": "New York/New Jersey", "capacity": 82500, "lat": 40.8135, "lng": -74.0745},
            {"name": "AT&T Stadium", "city": "Dallas", "capacity": 80000, "lat": 32.7473, "lng": -97.0929},
            {"name": "SoFi Stadium", "city": "Los Angeles", "capacity": 70000, "lat": 33.9534, "lng": -118.3391},
            {"name": "Mercedes-Benz Stadium", "city": "Atlanta", "capacity": 71000, "lat": 33.7551, "lng": -84.4009},
            {"name": "NRG Stadium", "city": "Houston", "capacity": 72220, "lat": 29.6848, "lng": -95.4109},
            {"name": "Lincoln Financial Field", "city": "Philadelphia", "capacity": 69596, "lat": 39.9005, "lng": -75.1675},
            {"name": "Lumen Field", "city": "Seattle", "capacity": 72000, "lat": 47.5952, "lng": -122.3316},
            {"name": "Levi's Stadium", "city": "San Francisco", "capacity": 68500, "lat": 37.4033, "lng": -121.9704},
            {"name": "Gillette Stadium", "city": "Boston", "capacity": 65878, "lat": 42.0909, "lng": -71.2643},
            {"name": "Hard Rock Stadium", "city": "Miami", "capacity": 65326, "lat": 25.9579, "lng": -80.2389},
            {"name": "Estadio Azteca", "city": "Mexico City", "capacity": 87523, "lat": 19.3030, "lng": -99.1504},
        ]
        stadiums = []
        for s in stadiums_data:
            stadium = Stadium(
                id=uuid.uuid4(),
                name=s["name"],
                city=s["city"],
                capacity=s["capacity"],
                latitude=s["lat"],
                longitude=s["lng"],
            )
            stadiums.append(stadium)
        db.add_all(stadiums)

        # --- Matches ---
        match_dates = [
            datetime(2026, 6, 11, 21, 0, tzinfo=timezone.utc),
            datetime(2026, 6, 12, 18, 0, tzinfo=timezone.utc),
            datetime(2026, 6, 13, 21, 0, tzinfo=timezone.utc),
        ]
        teams = [
            ("USA", "Mexico"), ("Brazil", "Argentina"),
            ("Germany", "France"), ("England", "Spain"),
        ]
        matches_data = [
            {"home": "USA", "away": "Mexico", "stadium": stadiums[0], "date": match_dates[0]},
            {"home": "Brazil", "away": "Argentina", "stadium": stadiums[2], "date": match_dates[0]},
            {"home": "Germany", "away": "France", "stadium": stadiums[6], "date": match_dates[1]},
            {"home": "England", "away": "Spain", "stadium": stadiums[3], "date": match_dates[2]},
        ]
        matches = []
        for m in matches_data:
            match = Match(
                id=uuid.uuid4(),
                home_team=m["home"],
                away_team=m["away"],
                stadium_id=m["stadium"].id,
                match_date=m["date"],
                status="scheduled",
                total_tickets=m["stadium"].capacity,
                sold_tickets=int(m["stadium"].capacity * 0.85),
            )
            matches.append(match)
        db.add_all(matches)

        # --- Crowd Data ---
        zones = ["Gate A", "Gate B", "Gate C", "Gate D", "Section 100", "Section 200", "Food Court", "Fan Zone"]
        now = datetime.now(timezone.utc)
        crowd_records = []
        for stadium in stadiums[:3]:
            for zone in zones:
                crowd = CrowdData(
                    id=uuid.uuid4(),
                    stadium_id=stadium.id,
                    zone=zone,
                    density=round(0.2 + 0.8 * (hash(zone + stadium.name) % 100) / 100, 2),
                    wait_time=5 + (hash(zone) % 30),
                    timestamp=now - timedelta(minutes=hash(zone) % 60),
                )
                crowd_records.append(crowd)
        db.add_all(crowd_records)

        # --- Routes ---
        routes_data = [
            {"name": "Main Entry → Section 100", "start": "Gate A", "end": "Section 100", "dist": 0.3, "wc": "yes"},
            {"name": "Parking Lot B → Gate C", "start": "Parking Lot B", "end": "Gate C", "dist": 0.8, "wc": "yes"},
            {"name": "Metro Station → Gate A", "start": "Metro Station", "end": "Gate A", "dist": 0.5, "wc": "no"},
            {"name": "Food Court → Section 200", "start": "Food Court", "end": "Section 200", "dist": 0.2, "wc": "yes"},
            {"name": "Bus Stop → Gate D", "start": "Bus Stop", "end": "Gate D", "dist": 0.6, "wc": "no"},
        ]
        route_entries = []
        for stadium in stadiums[:3]:
            for r in routes_data:
                route = Route(
                    id=uuid.uuid4(),
                    stadium_id=stadium.id,
                    name=r["name"],
                    start_location=r["start"],
                    end_location=r["end"],
                    distance_km=r["dist"],
                    wheelchair_accessible=r["wc"],
                )
                route_entries.append(route)
        db.add_all(route_entries)

        # --- Volunteers ---
        volunteer_zones = ["Gate A", "Gate B", "Fan Zone", "Section 100", "Parking"]
        volunteers = []
        for i, zone in enumerate(volunteer_zones):
            vol = Volunteer(
                id=uuid.uuid4(),
                user_id=staff.id if i == 0 else fan.id,
                zone=zone,
                status="available",
                is_active=True,
            )
            volunteers.append(vol)
        db.add_all(volunteers)

        # --- Incidents ---
        incidents = [
            Incident(
                id=uuid.uuid4(), reporter_id=staff.id,
                incident_type="medical", severity=2,
                description="Fan feeling dizzy at Section 100",
                location="Section 100, Row 15", status="in_progress",
            ),
            Incident(
                id=uuid.uuid4(), reporter_id=fan.id,
                incident_type="lost_child", severity=3,
                description="Lost child near Gate C, age 7, blue shirt",
                location="Gate C area", status="open",
            ),
            Incident(
                id=uuid.uuid4(), reporter_id=staff.id,
                incident_type="security", severity=1,
                description="Suspicious bag near entrance",
                location="Gate B", status="resolved",
            ),
        ]
        db.add_all(incidents)

        # --- Notifications ---
        notifications = [
            Notification(
                id=uuid.uuid4(), user_id=fan.id,
                title="Match Reminder",
                message="USA vs Mexico starts in 2 hours at MetLife Stadium.",
                notification_type="match", is_read=False,
            ),
            Notification(
                id=uuid.uuid4(), user_id=fan.id,
                title="Crowd Alert",
                message="Gate A is experiencing high traffic. Use Gate C instead.",
                notification_type="crowd", is_read=False,
            ),
            Notification(
                id=uuid.uuid4(), user_id=staff.id,
                title="Incident Assigned",
                message="Medical incident reported at Section 100. Please respond.",
                notification_type="incident", is_read=False,
            ),
        ]
        db.add_all(notifications)

        # --- Chat History ---
        chat = ChatHistory(
            id=uuid.uuid4(),
            session_id="demo-session",
            role="assistant",
            content="Welcome to StadiumAI! I'm your smart stadium assistant. I can help with navigation, match info, crowd conditions, and more. How can I help you today?",
        )
        db.add(chat)

        # --- AI Report ---
        report = AIReport(
            id=uuid.uuid4(),
            report_type="crowd_analysis",
            summary="Crowd density is currently moderate across all active stadiums. Gate A at MetLife is at 75% capacity. Recommend opening additional entry points.",
            recommendations="1. Open auxiliary gates at MetLife\n2. Deploy 5 more volunteers to Gate A\n3. Activate express entry for ticket holders",
        )
        db.add(report)

        # --- Transport Options ---
        transport_data = [
            {"stadium": stadiums[0], "type": "metro", "name": "Stadium Express", "status": "running", "next": "2 min", "wait": 2},
            {"stadium": stadiums[0], "type": "bus", "name": "Shuttle Bus 101", "status": "running", "next": "5 min", "wait": 5},
            {"stadium": stadiums[0], "type": "bus", "name": "Shuttle Bus 202", "status": "delayed", "next": "12 min", "wait": 12},
            {"stadium": stadiums[0], "type": "taxi", "name": "Taxi Stand", "status": "available", "next": "now", "wait": 0},
            {"stadium": stadiums[0], "type": "metro", "name": "City Line", "status": "running", "next": "4 min", "wait": 4},
            {"stadium": stadiums[1], "type": "bus", "name": "AT&T Shuttle", "status": "running", "next": "3 min", "wait": 3},
            {"stadium": stadiums[2], "type": "metro", "name": "SoFi Express", "status": "running", "next": "6 min", "wait": 6},
        ]
        transport_entries = []
        for t in transport_data:
            entry = TransportOption(
                id=uuid.uuid4(), stadium_id=t["stadium"].id,
                type=t["type"], name=t["name"], status=t["status"],
                next_arrival=t["next"], wait_minutes=t["wait"],
            )
            transport_entries.append(entry)
        db.add_all(transport_entries)

        # --- Parking Lots ---
        parking_data = [
            {"stadium": stadiums[0], "lot": "Lot A (East)", "available": 45, "total": 500, "dist": 50, "status": "filling"},
            {"stadium": stadiums[0], "lot": "Lot B (West)", "available": 210, "total": 500, "dist": 80, "status": "available"},
            {"stadium": stadiums[0], "lot": "Lot C (North)", "available": 340, "total": 600, "dist": 150, "status": "available"},
            {"stadium": stadiums[0], "lot": "VIP Parking", "available": 12, "total": 50, "dist": 20, "status": "limited"},
            {"stadium": stadiums[1], "lot": "AT&T Garage A", "available": 180, "total": 800, "dist": 60, "status": "available"},
            {"stadium": stadiums[2], "lot": "SoFi Parking", "available": 90, "total": 700, "dist": 100, "status": "filling"},
        ]
        parking_entries = []
        for p in parking_data:
            lot = ParkingLot(
                id=uuid.uuid4(), stadium_id=p["stadium"].id,
                lot=p["lot"], available_spots=p["available"],
                total_spots=p["total"], distance_m=p["dist"], status=p["status"],
            )
            parking_entries.append(lot)
        db.add_all(parking_entries)

        # --- Sustainability Logs ---
        sustainability_data = [
            {"stadium": stadiums[0], "metric": "waste_generated", "value": 2.4, "unit": "tonnes"},
            {"stadium": stadiums[0], "metric": "water_usage", "value": 18.5, "unit": "kL"},
            {"stadium": stadiums[0], "metric": "electricity", "value": 142, "unit": "MWh"},
            {"stadium": stadiums[0], "metric": "recycled_waste", "value": 65, "unit": "%"},
            {"stadium": stadiums[0], "metric": "carbon_footprint", "value": 12.8, "unit": "tCO2e"},
            {"stadium": stadiums[0], "metric": "solar_generated", "value": 8.2, "unit": "MWh"},
        ]
        sustainability_entries = []
        for s in sustainability_data:
            log = SustainabilityLog(
                id=uuid.uuid4(), stadium_id=s["stadium"].id,
                metric_type=s["metric"], value=s["value"], unit=s["unit"],
            )
            sustainability_entries.append(log)
        db.add_all(sustainability_entries)

        db.commit()
        print(f"Database seeded successfully!")
        print(f"  - {len(stadiums_data)} stadiums")
        print(f"  - {len(matches_data)} matches")
        print(f"  - {len(crowd_records)} crowd data points")
        print(f"  - {len(route_entries)} routes")
        print(f"  - {len(volunteers)} volunteers")
        print(f"  - {len(incidents)} incidents")
        print(f"  - {len(notifications)} notifications")
        print(f"  - {len(transport_entries)} transport options")
        print(f"  - {len(parking_entries)} parking lots")
        print(f"  - {len(sustainability_entries)} sustainability logs")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
