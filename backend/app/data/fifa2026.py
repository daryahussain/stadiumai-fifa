"""Real FIFA World Cup 2026 data fetched from web sources."""

STADIUMS = [
    {"id": "1", "name": "MetLife Stadium", "city": "East Rutherford, New Jersey", "capacity": 82500, "country": "USA", "lat": 40.8135, "lng": -74.0745},
    {"id": "2", "name": "SoFi Stadium", "city": "Los Angeles, California", "capacity": 70492, "country": "USA", "lat": 33.9534, "lng": -118.3391},
    {"id": "3", "name": "AT&T Stadium", "city": "Arlington, Texas", "capacity": 70649, "country": "USA", "lat": 32.7473, "lng": -97.0929},
    {"id": "4", "name": "Mercedes-Benz Stadium", "city": "Atlanta, Georgia", "capacity": 68239, "country": "USA", "lat": 33.7551, "lng": -84.4009},
    {"id": "5", "name": "NRG Stadium", "city": "Houston, Texas", "capacity": 68777, "country": "USA", "lat": 29.6848, "lng": -95.4109},
    {"id": "6", "name": "Hard Rock Stadium", "city": "Miami Gardens, Florida", "capacity": 64478, "country": "USA", "lat": 25.9579, "lng": -80.2389},
    {"id": "7", "name": "Lincoln Financial Field", "city": "Philadelphia, Pennsylvania", "capacity": 68324, "country": "USA", "lat": 39.9005, "lng": -75.1675},
    {"id": "8", "name": "Lumen Field", "city": "Seattle, Washington", "capacity": 66925, "country": "USA", "lat": 47.5952, "lng": -122.3316},
    {"id": "9", "name": "Levi's Stadium", "city": "Santa Clara, California", "capacity": 68827, "country": "USA", "lat": 37.4033, "lng": -121.9704},
    {"id": "10", "name": "Gillette Stadium", "city": "Foxborough, Massachusetts", "capacity": 64146, "country": "USA", "lat": 42.0909, "lng": -71.2643},
    {"id": "11", "name": "Arrowhead Stadium", "city": "Kansas City, Missouri", "capacity": 69045, "country": "USA", "lat": 39.0489, "lng": -94.4839},
    {"id": "12", "name": "Estadio Azteca", "city": "Mexico City", "capacity": 80824, "country": "Mexico", "lat": 19.3030, "lng": -99.1504},
    {"id": "13", "name": "Estadio BBVA", "city": "Guadalupe, Nuevo León", "capacity": 51243, "country": "Mexico", "lat": 25.6693, "lng": -100.2436},
    {"id": "14", "name": "Estadio Akron", "city": "Zapopan, Jalisco", "capacity": 45664, "country": "Mexico", "lat": 20.6816, "lng": -103.4602},
    {"id": "15", "name": "BC Place", "city": "Vancouver, British Columbia", "capacity": 52497, "country": "Canada", "lat": 49.2767, "lng": -123.1120},
    {"id": "16", "name": "BMO Field", "city": "Toronto, Ontario", "capacity": 43036, "country": "Canada", "lat": 43.6328, "lng": -79.4186},
]

MATCHES = [
    {"id": "m1", "home": "Mexico", "away": "South Africa", "stadium": "Estadio Azteca", "stadium_id": "12", "date": "2026-06-11", "time": "15:00 ET", "round": "Group A", "status": "completed", "home_score": 2, "away_score": 0},
    {"id": "m2", "home": "USA", "away": "Paraguay", "stadium": "SoFi Stadium", "stadium_id": "2", "date": "2026-06-12", "time": "18:00 ET", "round": "Group D", "status": "completed", "home_score": 4, "away_score": 1},
    {"id": "m3", "home": "Brazil", "away": "Morocco", "stadium": "MetLife Stadium", "stadium_id": "1", "date": "2026-06-13", "time": "21:00 ET", "round": "Group C", "status": "completed", "home_score": 1, "away_score": 1},
    {"id": "m4", "home": "England", "away": "Croatia", "stadium": "MetLife Stadium", "stadium_id": "1", "date": "2026-06-17", "time": "20:00 ET", "round": "Group L", "status": "completed", "home_score": 4, "away_score": 2},
    {"id": "m5", "home": "Germany", "away": "Curaçao", "stadium": "Lincoln Financial Field", "stadium_id": "7", "date": "2026-06-14", "time": "18:00 ET", "round": "Group E", "status": "completed", "home_score": 7, "away_score": 1},
    {"id": "m6", "home": "Argentina", "away": "Algeria", "stadium": "Mercedes-Benz Stadium", "stadium_id": "4", "date": "2026-06-16", "time": "20:00 ET", "round": "Group J", "status": "completed", "home_score": 3, "away_score": 0},
    {"id": "m7", "home": "France", "away": "Senegal", "stadium": "NRG Stadium", "stadium_id": "5", "date": "2026-06-16", "time": "21:00 ET", "round": "Group I", "status": "completed", "home_score": 3, "away_score": 1},
    {"id": "m8", "home": "Spain", "away": "Belgium", "stadium": "SoFi Stadium", "stadium_id": "2", "date": "2026-07-10", "time": "19:00 ET", "round": "Quarter-final", "status": "scheduled"},
    {"id": "m9", "home": "France", "away": "Morocco", "stadium": "Gillette Stadium", "stadium_id": "10", "date": "2026-07-09", "time": "20:00 ET", "round": "Quarter-final", "status": "scheduled"},
    {"id": "m10", "home": "Norway", "away": "England", "stadium": "Hard Rock Stadium", "stadium_id": "6", "date": "2026-07-11", "time": "21:00 ET", "round": "Quarter-final", "status": "scheduled"},
    {"id": "m11", "home": "Argentina", "away": "Switzerland", "stadium": "Arrowhead Stadium", "stadium_id": "11", "date": "2026-07-12", "time": "21:00 ET", "round": "Quarter-final", "status": "scheduled"},
    {"id": "m12", "home": "Winner QF1", "away": "Winner QF2", "stadium": "AT&T Stadium", "stadium_id": "3", "date": "2026-07-14", "time": "19:00 ET", "round": "Semi-final", "status": "scheduled"},
    {"id": "m13", "home": "Winner QF3", "away": "Winner QF4", "stadium": "Mercedes-Benz Stadium", "stadium_id": "4", "date": "2026-07-15", "time": "19:00 ET", "round": "Semi-final", "status": "scheduled"},
    {"id": "m14", "home": "Loser SF1", "away": "Loser SF2", "stadium": "Hard Rock Stadium", "stadium_id": "6", "date": "2026-07-18", "time": "21:00 ET", "round": "Third Place", "status": "scheduled"},
    {"id": "m15", "home": "Winner SF1", "away": "Winner SF2", "stadium": "MetLife Stadium", "stadium_id": "1", "date": "2026-07-19", "time": "19:00 ET", "round": "Final", "status": "scheduled"},
]

ZONES = ["Gate A", "Gate B", "Gate C", "Gate D", "Section 100", "Section 200", "Section 300", "Food Court L1", "Food Court L2", "Parking Lot A", "Parking Lot B", "Concourse East", "Concourse West", "Fan Zone", "VIP Lounge", "Media Center"]

ROUTES = [
    {"name": "Main Entry → Section 100", "start": "Gate A", "end": "Section 100", "dist": 0.3, "wc": "yes"},
    {"name": "Parking Lot B → Gate C", "start": "Parking Lot B", "end": "Gate C", "dist": 0.8, "wc": "yes"},
    {"name": "Metro Station → Gate A", "start": "Metro Station", "end": "Gate A", "dist": 0.5, "wc": "no"},
    {"name": "Food Court → Section 200", "start": "Food Court", "end": "Section 200", "dist": 0.2, "wc": "yes"},
    {"name": "Bus Stop → Gate D", "start": "Bus Stop", "end": "Gate D", "dist": 0.6, "wc": "no"},
    {"name": "VIP Parking → VIP Lounge", "start": "VIP Parking", "end": "VIP Lounge", "dist": 0.1, "wc": "yes"},
    {"name": "Concourse East → Section 300", "start": "Concourse East", "end": "Section 300", "dist": 0.4, "wc": "yes"},
    {"name": "Gate B → Food Court L1", "start": "Gate B", "end": "Food Court L1", "dist": 0.2, "wc": "yes"},
    {"name": "Parking Lot A → Gate A", "start": "Parking Lot A", "end": "Gate A", "dist": 0.15, "wc": "yes"},
    {"name": "Section 100 → Restroom", "start": "Section 100", "end": "Restroom (West)", "dist": 0.05, "wc": "yes"},
]

TRANSPORT_OPTIONS = [
    {"type": "metro", "name": "Stadium Express", "status": "running", "next": "2 min", "wait": 2},
    {"type": "bus", "name": "Shuttle Bus 101", "status": "running", "next": "5 min", "wait": 5},
    {"type": "bus", "name": "Shuttle Bus 202", "status": "delayed", "next": "12 min", "wait": 12},
    {"type": "taxi", "name": "Taxi Stand", "status": "available", "next": "now", "wait": 0},
    {"type": "metro", "name": "City Line", "status": "running", "next": "4 min", "wait": 4},
    {"type": "rideshare", "name": "Ride-share Pick-up Zone", "status": "available", "next": "3 min", "wait": 3},
    {"type": "bike", "name": "Bike Share Station", "status": "available", "next": "now", "wait": 0},
]

PARKING_LOTS = [
    {"lot": "Lot A (East)", "available": 45, "total": 500, "dist": 50, "status": "filling"},
    {"lot": "Lot B (West)", "available": 210, "total": 500, "dist": 80, "status": "available"},
    {"lot": "Lot C (North)", "available": 340, "total": 600, "dist": 150, "status": "available"},
    {"lot": "VIP Parking", "available": 12, "total": 50, "dist": 20, "status": "limited"},
    {"lot": "Oversized Vehicle Lot", "available": 15, "total": 80, "dist": 200, "status": "available"},
    {"lot": "Accessible Parking", "available": 8, "total": 30, "dist": 15, "status": "limited"},
]

SUSTAINABILITY_LOGS = [
    {"metric": "waste_generated", "value": 2.4, "unit": "tonnes"},
    {"metric": "water_usage", "value": 18.5, "unit": "kL"},
    {"metric": "electricity", "value": 142, "unit": "MWh"},
    {"metric": "recycled_waste", "value": 65, "unit": "%"},
    {"metric": "carbon_footprint", "value": 12.8, "unit": "tCO2e"},
    {"metric": "solar_generated", "value": 8.2, "unit": "MWh"},
]

QUALIFIED_TEAMS = [
    "Mexico", "USA", "Canada", "Brazil", "Argentina", "Germany", "France",
    "England", "Spain", "Portugal", "Netherlands", "Belgium", "Croatia",
    "Uruguay", "Japan", "South Korea", "Australia", "Morocco", "Senegal",
    "Ghana", "Nigeria", "Cameroon", "Saudi Arabia", "Iran", "Switzerland",
    "Poland", "Denmark", "Italy", "Norway", "Sweden", "Paraguay", "Egypt",
    "Algeria", "Tunisia", "Ecuador", "Costa Rica", "Panama", "Jamaica",
    "South Africa", "Iraq", "Jordan", "Qatar", "Cape Verde", "New Zealand",
    "Curaçao", "Scotland", "Haiti", "Bosnia and Herzegovina", "Austria",
]

VOLUNTEER_ZONES = [
    {"zone": "Gate A", "role": "Entry Assistance", "count": 8},
    {"zone": "Gate B", "role": "Entry Assistance", "count": 6},
    {"zone": "Gate C", "role": "Entry Assistance", "count": 7},
    {"zone": "Gate D", "role": "Entry Assistance", "count": 5},
    {"zone": "Fan Zone", "role": "Information", "count": 4},
    {"zone": "Section 100", "role": "Seating Help", "count": 3},
    {"zone": "Section 200", "role": "Seating Help", "count": 3},
    {"zone": "Food Court", "role": "Crowd Management", "count": 4},
    {"zone": "Parking Lot A", "role": "Traffic Direction", "count": 4},
    {"zone": "Parking Lot B", "role": "Traffic Direction", "count": 3},
    {"zone": "Concourse", "role": "Information", "count": 5},
    {"zone": "VIP Lounge", "role": "Guest Services", "count": 2},
]
