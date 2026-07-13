from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.route import Route
from app.models.crowd_data import CrowdData
from app.schemas.navigation import RouteRequest, RouteResponse, RouteStep, GateInfo, NavigationData
from app.data import fifa2026

router = APIRouter()

_DEFAULT_AMENITIES = [
    "ATM - Near Gate A", "ATM - Near Gate C",
    "Baby Care - Restroom North", "Baby Care - Restroom South",
    "Charging Station - Food Court",
    "Lost & Found - Guest Services",
    "Wheelchair Rental - Main Entrance",
    "First Aid - Medical Station",
    "Info Desk - Main Concourse",
]


def _build_route_response(start: str, end: str, dist_km: float, wc: str) -> RouteResponse:
    total_dist_m = int(dist_km * 1000)
    estimated_min = max(1, total_dist_m // 80)
    return RouteResponse(
        from_location=start,
        to_location=end,
        total_distance_m=total_dist_m,
        estimated_minutes=estimated_min,
        steps=[
            RouteStep(instruction=f"Head from {start} towards the main concourse", distance_m=total_dist_m // 2, landmark="Main Concourse"),
            RouteStep(instruction=f"Continue to {end}", distance_m=total_dist_m // 2, landmark=end),
        ],
        wheelchair_accessible=wc == "yes",
    )


def _crowd_level(density: float) -> str:
    if density >= 0.7:
        return "high"
    if density <= 0.4:
        return "low"
    return "moderate"


@router.post("/route")
async def get_route(body: RouteRequest, db: Session = Depends(get_db)):
    route = db.query(Route).filter(
        Route.start_location == body.from_location,
        Route.end_location == body.to_location,
    ).first()

    if route:
        return _build_route_response(route.start_location, route.end_location, route.distance_km or 0.5, route.wheelchair_accessible or "no")

    for r in fifa2026.ROUTES:
        if r["start"].lower() == body.from_location.lower() and r["end"].lower() == body.to_location.lower():
            return _build_route_response(r["start"], r["end"], r["dist"], r["wc"])

    raise HTTPException(status_code=404, detail="No route found between these locations")


@router.get("/data")
async def get_navigation_data(db: Session = Depends(get_db)):
    routes = db.query(Route).all()

    if not routes:
        zones = list(set(r["start"] for r in fifa2026.ROUTES) | set(r["end"] for r in fifa2026.ROUTES))
        return NavigationData(
            zones=sorted(zones),
            gates=[
                GateInfo(gate="Gate A", recommended_for=["Sections 100-200"], distance_m=50, crowd_level="moderate"),
                GateInfo(gate="Gate B", recommended_for=["Sections 200-300", "Food Court"], distance_m=80, crowd_level="low"),
                GateInfo(gate="Gate C", recommended_for=["VIP", "Press"], distance_m=120, crowd_level="low"),
                GateInfo(gate="Gate D", recommended_for=["Parking Lot B"], distance_m=200, crowd_level="moderate"),
            ],
            amenities=_DEFAULT_AMENITIES,
        )

    locations: set[str] = set()
    for r in routes:
        locations.add(r.start_location)
        locations.add(r.end_location)

    gate_names = sorted({r.start_location for r in routes if r.start_location.startswith("Gate")})

    crowd_map = {}
    if gate_names:
        from sqlalchemy import func as sa_func
        subq = (
            db.query(CrowdData.zone, sa_func.max(CrowdData.timestamp).label("max_ts"))
            .filter(CrowdData.zone.in_(gate_names))
            .group_by(CrowdData.zone)
            .subquery()
        )
        latest = (
            db.query(CrowdData.zone, CrowdData.density)
            .join(subq, (CrowdData.zone == subq.c.zone) & (CrowdData.timestamp == subq.c.max_ts))
            .all()
        )
        crowd_map = {z: d for z, d in latest}

    gates = [
        GateInfo(gate=name, recommended_for=[], distance_m=50, crowd_level=_crowd_level(crowd_map.get(name, 0.5)))
        for name in gate_names
    ]

    return NavigationData(zones=sorted(locations), gates=gates, amenities=_DEFAULT_AMENITIES)
