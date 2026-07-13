from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.transport_option import TransportOption as TransportModel, ParkingLot
from app.schemas.transport import TransportResponse, TransportOption as TransportSchema, ParkingInfo
from app.data import fifa2026

router = APIRouter()


@router.get("/")
async def get_transport(db: Session = Depends(get_db)):
    transport_records = db.query(TransportModel).all()
    parking_records = db.query(ParkingLot).all()

    if not transport_records and not parking_records:
        return TransportResponse(
            options=[
                TransportSchema(name=t["name"], type=t["type"], status=t["status"], next_arrival=t["next"], wait_minutes=t["wait"])
                for t in fifa2026.TRANSPORT_OPTIONS
            ],
            parking=[
                ParkingInfo(lot=p["lot"], available_spots=p["available"], total_spots=p["total"],
                            distance_m=p["dist"], status=p["status"])
                for p in fifa2026.PARKING_LOTS
            ],
            ai_recommendation="Stadium Express Metro is running on schedule. Shuttle Bus 202 is experiencing minor delays. Parking Lots A and B have available spaces.",
        )

    return TransportResponse(
        options=[
            TransportSchema(name=t.name, type=t.type, status=t.status, next_arrival=t.next_arrival, wait_minutes=t.wait_minutes)
            for t in transport_records
        ],
        parking=[
            ParkingInfo(lot=p.lot, available_spots=p.available_spots, total_spots=p.total_spots,
                        distance_m=p.distance_m, status=p.status)
            for p in parking_records
        ],
        ai_recommendation="All transport options are operating normally.",
    )
