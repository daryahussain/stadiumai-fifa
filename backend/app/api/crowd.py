from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.crowd_data import CrowdData
from app.models.stadium import Stadium
from app.models.ai_report import AIReport
from app.schemas.crowd import CrowdResponse, CrowdOverview, ZoneDensity, QueueInfo

router = APIRouter()


def _status_label(density: float) -> str:
    if density >= 0.8:
        return "congested"
    if density >= 0.6:
        return "busy"
    if density >= 0.4:
        return "moderate"
    return "clear"


@router.get("/")
async def get_crowd_data(db: Session = Depends(get_db)):
    records = db.query(CrowdData).order_by(CrowdData.timestamp.desc()).limit(50).all()
    stadiums = db.query(Stadium).all()
    total_capacity = sum(s.capacity for s in stadiums)

    latest_per_zone = {}
    for r in records:
        if r.zone not in latest_per_zone:
            latest_per_zone[r.zone] = r

    zones = [
        ZoneDensity(
            zone=r.zone,
            density=round(r.density * 100, 1),
            status=_status_label(r.density),
            wait_time=r.wait_time or 0,
        )
        for r in latest_per_zone.values()
    ]
    avg_density = round(sum(z.density for z in zones) / len(zones), 1) if zones else 0.0
    total_occupancy = int(total_capacity * avg_density / 100) if total_capacity else 0

    latest_report = db.query(AIReport).filter(AIReport.report_type == "crowd_analysis").order_by(AIReport.generated_at.desc()).first()

    return CrowdResponse(
        overview=CrowdOverview(
            total_occupancy=total_occupancy,
            total_capacity=total_capacity,
            avg_density=avg_density,
            congestion_level=_status_label(avg_density / 100),
        ),
        zones=zones,
        queues=[
            QueueInfo(location=z.zone, type="entry", wait_minutes=z.wait_time, trend="stable")
            for z in zones[:5]
        ],
        ai_summary=latest_report.summary if latest_report else "No crowd analysis available.",
    )
