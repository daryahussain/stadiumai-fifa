from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.transport_option import TransportOption, ParkingLot
from app.models.ai_report import AIReport
from app.schemas.transport import TransportResponse, TransportOption as TransportOptionSchema, ParkingInfo

router = APIRouter()


@router.get("/")
async def get_transport(db: Session = Depends(get_db)):
    options = db.query(TransportOption).limit(10).all()
    parking = db.query(ParkingLot).limit(10).all()

    latest_report = db.query(AIReport).filter(AIReport.report_type == "transport").order_by(AIReport.generated_at.desc()).first()

    return TransportResponse(
        options=[
            TransportOptionSchema(
                type=o.type, name=o.name, status=o.status,
                next_arrival=o.next_arrival, wait_minutes=o.wait_minutes,
            )
            for o in options
        ],
        parking=[
            ParkingInfo(
                lot=p.lot, available_spots=p.available_spots,
                total_spots=p.total_spots, distance_m=p.distance_m, status=p.status,
            )
            for p in parking
        ],
        ai_recommendation=latest_report.summary if latest_report else "All transport options are operating normally.",
    )
