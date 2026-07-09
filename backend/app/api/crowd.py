from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.crowd_data import CrowdData
from app.models.stadium import Stadium
from app.models.ai_report import AIReport
from app.schemas.crowd import CrowdResponse, CrowdOverview, ZoneDensity, QueueInfo
from app.data import fifa2026

router = APIRouter()


def _status_label(density: float) -> str:
    if density >= 0.8:
        return "congested"
    if density >= 0.6:
        return "busy"
    if density >= 0.4:
        return "moderate"
    return "clear"


def _build_fallback_crowd() -> CrowdResponse:
    import random
    zones = []
    for z in fifa2026.ZONES:
        density = round(random.uniform(15, 85), 1)
        zones.append(ZoneDensity(
            zone=z,
            density=density,
            status=_status_label(density / 100),
            wait_time=random.randint(2, 25),
        ))
    avg = round(sum(z.density for z in zones) / len(zones), 1)
    total_cap = sum(s["capacity"] for s in fifa2026.STADIUMS)
    return CrowdResponse(
        overview=CrowdOverview(
            total_occupancy=int(total_cap * avg / 100),
            total_capacity=total_cap,
            avg_density=avg,
            congestion_level=_status_label(avg / 100),
        ),
        zones=zones,
        queues=[QueueInfo(location=z.zone, type="entry", wait_minutes=z.wait_time, trend="stable") for z in zones[:5]],
        ai_summary=(
            f"Crowd density is currently {avg}% across all active stadiums. "
            f"{'Gate areas are busy — consider using less congested entry points.' if avg > 60 else 'Traffic is flowing smoothly across all venues.'} "
            f"The quarter-finals are ongoing with France vs Morocco tonight at Gillette Stadium."
        ),
    )


@router.get("/")
async def get_crowd_data(db: Session = Depends(get_db)):
    records = db.query(CrowdData).order_by(CrowdData.timestamp.desc()).limit(50).all()
    stadiums = db.query(Stadium).all()

    if not records and not stadiums:
        return _build_fallback_crowd()

    total_capacity = sum(s.capacity for s in stadiums) if stadiums else sum(s["capacity"] for s in fifa2026.STADIUMS)

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
        ai_summary=latest_report.summary if latest_report else "Live crowd data streaming. Current conditions vary by zone.",
    )
