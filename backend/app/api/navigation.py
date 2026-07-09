from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.route import Route
from app.models.crowd_data import CrowdData
from app.schemas.navigation import RouteRequest, RouteResponse, RouteStep, GateInfo, NavigationData
from app.data import fifa2026

router = APIRouter()


@router.post("/route")
async def get_route(body: RouteRequest, db: Session = Depends(get_db)):
    route = db.query(Route).filter(
        Route.start_location == body.from_location,
        Route.end_location == body.to_location,
    ).first()

    if not route:
        for r in fifa2026.ROUTES:
            if r["start"].lower() == body.from_location.lower() and r["end"].lower() == body.to_location.lower():
                dist = r["dist"]
                total_dist_m = int(dist * 1000)
                estimated_min = max(1, total_dist_m // 80)
                return RouteResponse(
                    from_location=r["start"],
                    to_location=r["end"],
                    total_distance_m=total_dist_m,
                    estimated_minutes=estimated_min,
                    steps=[
                        RouteStep(instruction=f"Head from {r['start']} towards the main concourse", distance_m=total_dist_m // 2, landmark="Main Concourse"),
                        RouteStep(instruction=f"Continue to {r['end']}", distance_m=total_dist_m // 2, landmark=r["end"]),
                    ],
                    wheelchair_accessible=r["wc"] == "yes",
                )
        raise HTTPException(status_code=404, detail="No route found between these locations")

    total_dist_m = int((route.distance_km or 0.5) * 1000)
    estimated_min = max(1, total_dist_m // 80)

    steps = [
        RouteStep(
            instruction=f"Head from {route.start_location} towards the main concourse",
            distance_m=total_dist_m // 2,
            landmark="Main Concourse",
        ),
        RouteStep(
            instruction=f"Continue to {route.end_location}",
            distance_m=total_dist_m // 2,
            landmark=route.end_location,
        ),
    ]

    return RouteResponse(
        from_location=route.start_location,
        to_location=route.end_location,
        total_distance_m=total_dist_m,
        estimated_minutes=estimated_min,
        steps=steps,
        wheelchair_accessible=route.wheelchair_accessible == "yes",
    )


@router.get("/data")
async def get_navigation_data(db: Session = Depends(get_db)):
    routes = db.query(Route).all()

    if not routes:
        zones = list(set(r["start"] for r in fifa2026.ROUTES) | set(r["end"] for r in fifa2026.ROUTES))
        return NavigationData(
            zones=sorted(zones),
            gates=[GateInfo(gate="Gate A", recommended_for=["Sections 100-200"], distance_m=50, crowd_level="moderate"),
                   GateInfo(gate="Gate B", recommended_for=["Sections 200-300", "Food Court"], distance_m=80, crowd_level="low"),
                   GateInfo(gate="Gate C", recommended_for=["VIP", "Press"], distance_m=120, crowd_level="low"),
                   GateInfo(gate="Gate D", recommended_for=["Parking Lot B"], distance_m=200, crowd_level="moderate")],
            amenities=[
                "ATM - Near Gate A", "ATM - Near Gate C",
                "Baby Care - Restroom North", "Baby Care - Restroom South",
                "Charging Station - Food Court",
                "Lost & Found - Guest Services",
                "Wheelchair Rental - Main Entrance",
                "First Aid - Medical Station",
                "Info Desk - Main Concourse",
            ],
        )

    locations = set()
    for r in routes:
        locations.add(r.start_location)
        locations.add(r.end_location)

    zones = sorted(locations)
    gates_data = db.query(Route).filter(Route.start_location.like("Gate%")).all()
    seen_gates = set()
    gates = []
    for r in gates_data:
        gate_name = r.start_location
        if gate_name not in seen_gates:
            seen_gates.add(gate_name)
            crowd = db.query(CrowdData).filter(CrowdData.zone == gate_name).order_by(CrowdData.timestamp.desc()).first()
            level = "moderate"
            if crowd:
                if crowd.density >= 0.7:
                    level = "high"
                elif crowd.density <= 0.4:
                    level = "low"
            gates.append(GateInfo(gate=gate_name, recommended_for=[], distance_m=50, crowd_level=level))

    amenities = [
        "ATM - Near Gate A", "ATM - Near Gate C",
        "Baby Care - Restroom North", "Baby Care - Restroom South",
        "Charging Station - Food Court",
        "Lost & Found - Guest Services",
        "Wheelchair Rental - Main Entrance",
        "First Aid - Medical Station",
        "Info Desk - Main Concourse",
    ]

    return NavigationData(zones=zones, gates=gates, amenities=amenities)
